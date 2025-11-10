# myapp/views.py
from django.shortcuts import render
from .utils import *
from uploads.forms import UploadFileForm

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContextQuerySerializer
from .serializers import HITLFeedbackSerializer
from .ai_helpers import call_cohere_api, call_gemini_api
from uploads.utils import preprocess, extract_docx_content, extract_images
import json
from PyPDF2 import PdfReader
from .prompts import prompt_library
from uploads.models import FileModel
from classification.services.classification_logic import classify_document 
from classification.services.pii_detection import detect_pii_pdf, detect_pii_docx
from uploads.utils import extract_docx_content

def get_document_analysis(document_id):
    """
    Enhanced helper function that uses your existing processing logic
    """
    try:
        file_obj = FileModel.objects.get(id=document_id)
        uploaded_file = file_obj.file
        
        # Use your existing preprocessing logic
        preprocessed_file = preprocess(uploaded_file)
        
        # Extract text based on file type
        text_content = ""
        if preprocessed_file["is_pdf"]:
            uploaded_file.open('rb')
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text_content += page.extract_text() or ""
            text_content = text_content.strip()
            uploaded_file.close()
            
            pii_flags = detect_pii_pdf(uploaded_file)
        else:  # docx
            text_content, images = extract_docx_content(uploaded_file)
            preprocessed_file["num_images"] = len(images)
            pii_flags = detect_pii_docx(text_content, images)
        
        # Classify using your existing logic
        category = classify_document(
            text_content, 
            pii_flags, 
            preprocessed_file["num_pages"], 
            preprocessed_file.get("num_images", 0), 
            preprocessed_file.get("images", [])
        )
        
        return {
            'category': category,
            'flags': pii_flags,
            'metadata': {
                'num_pages': preprocessed_file["num_pages"],
                'num_images': preprocessed_file.get("num_images", 0),
                'file_size': uploaded_file.size,
                'title': file_obj.title,
            },
            'citations': [],  # Add if you have citation extraction
            'text_content': text_content  # Include for reference
        }
    except FileModel.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error analyzing document {document_id}: {str(e)}")
        return None


class ContextQueryView(APIView):
    def post(self, request, format=None):
        serializer = ContextQuerySerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            document_id = serializer.validated_data.get('document_id', None)
            #if there is no doc id
            if document_id is None:
                return Response(
                    {"error": "Missing Document ID in request."},
                    status =  status.HTTP_400_BAD_REQUEST
                )
            # call document classifer 
            doc_analysis = get_document_analysis(document_id)
            category = doc_analysis.get('categories', [])
            prompt_sequence = []
            for cat in category:
                prompt_sequence.extend(prompt_library.get(cat, []))
            if "root" in prompt_library:
                prompt_sequence.insert(0, prompt_library["root"])
            prompt_sequence = list(dict.fromkeys(prompt_sequence)) #deduplicate
            
            # and context assembler
            
            #if category is empty
            if category==[]:
                return Response(
                    {"error": "Document not found or Classification of document has failed."},
                    status =  status.HTTP_400_BAD_REQUEST
                )
            flags = doc_analysis.get('flags', [])
            edge_case = bool(flags)
            package = {
                'query': query,
                'document':{
                    'category': category,
                    "metadata": doc_analysis.get('metadata', {}),
                    "citations": doc_analysis.get('citations', []),
                    "flags": flags,
                },
                'edge_case': edge_case,
                'status': "Flagged: Sensitive content" if flags else "OK",
                'prompt_sequence': prompt_sequence,
            }
            try: 
                cohere_result = call_cohere_api(package)
            except Exception as e:
                return Response(
                    {"error": "Cohere API call failed", "details": str(e)},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            try:
                gemini_result = call_gemini_api(package)
            except Exception as e:
                return Response(
                    {"error": "Gemini API call failed", "details": str(e)},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            c_conf = cohere_result.get('confidence')
            g_conf = gemini_result.get('confidence')
            if c_conf is None or g_conf is None:
                return Response(
                    {"error": "Invalid response from AI services"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            diff = abs(c_conf-g_conf)
            consensus = "disagree"
            if diff<0.10:
                consensus = "agree"
            response = {
                "package": package,
                "cohere_result": cohere_result,
                "gemini_result": gemini_result,
                "consensus": consensus

            }
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid request data', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST)

class HITLFeedbackView(APIView):
    def post(self, request, format = None):
        serializer = HITLFeedbackSerializer(data = request.data)
        if serializer.is_valid():
            updates = serializer.validated_data
            query = updates['query']
            document_id = updates['document_id']
            #original package
            original_data = classify_document(document_id)
            #build original package
            original_package = {
                'document':{
                    'query': query,
                    'id': document_id,
                    'category': original_data.get('category'),
                    "metadata": original_data.get('metadata', {}),
                    "citations": original_data.get('citations', []),
                    "flags": original_data.get('flags', []),
                },
                #what goes in here?
                'edge_case': bool(original_data.get('flags', [])),
                'status': "Flagged: Sensitive content" if original_data.get('flags') else "OK",
                'prompt_sequence': [],
            }
            corrected_package = original_package.copy()
            corrected_categories = updates.get('categories', [original_data.get('category')])
            for key, value in updates.items():
                if value is not None and key!='document_id':
                    corrected_package[key] = value
            #store or log second for audit trail
            with open("hitl_feedback_log.txt", "a") as log:
                log.write(json.dumps({
                    "original_package": original_package,
                    "corrected_package": corrected_package
                }) + "\n")
            #rebuild prompt sequence if categories updated
            prompt_sequence = []
            for cat in corrected_categories:
                prompt_sequence.extend(prompt_library.get(cat, []))
            if "root" in prompt_library:
                prompt_sequence.insert(0, prompt_library["root"])
            prompt_sequence = list(dict.fromkeys(prompt_sequence)) #deduplicate
            corrected_package['prompt_sequence'] = prompt_sequence
            try: 
                cohere_result = call_cohere_api(corrected_package)
            except Exception as e:
                return Response(
                    {"error": "Cohere API call failed", "details": str(e)},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            try:
                gemini_result = call_gemini_api(corrected_package)
            except Exception as e:
                return Response(
                    {"error": "Gemini API call failed", "details": str(e)},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            c_conf = cohere_result.get('confidence')
            g_conf = gemini_result.get('confidence')
            if c_conf is None or g_conf is None:
                return Response(
                    {"error": "Invalid response from AI services"},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            diff = abs(c_conf-g_conf)
            consensus = "disagree"
            if diff<0.10:
                consensus = "agree"
            
            return Response({
                'corrected_package': corrected_package,
                "cohere_result": cohere_result,
                "gemini_result": gemini_result,
                "consensus": consensus,
                "message": "Corrections applied.",
            }, status = status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid request data', 'details': serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST)