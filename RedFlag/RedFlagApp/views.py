# myapp/views.py
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileModel # Assuming you have a model to store file info
from .utils import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ContextQuerySerializer
from .serializers import HITLFeedbackSerializer
from .ai_helpers import call_cohere_api, call_gemini_api
import json
from .prompts import prompt_library
def mock_external_api(query):
    #simulate different apis or queries 
    if 'notion' in query.lower():
        return {
            'notion_summary' : 'summary from notion api '
        }
    return {'external info': 'no matching external data found'}



def mock_classify_document(document_id):
    #this is temporary, in a real system you'd look up uploaded file and run classifier
    #simulate a few cases
    mock_results = {
        1:{
            "category": "Public",
            "citations": ["page 1: SSN field", "image 3: face detected"],
            "flags": [],
            "metadata" :{"pages": 3, "images": 1}
        },
        2:{
            "category": "Highly Sensitive",
            "citations": ["page 2: SSN field"],
            "flags": ["PII detected", "Needs Redaction"],
            "metadata" :{"pages": 2, "images": 0}
        },
        3:{
            "category": "Confidential",
            "citations": ["page 1: Project details"],
            "flags": ["Internal Only"],
            "metadata" :{"pages": 1, "images": 0}
        },

    }
    return mock_results.get(document_id, {
            "category": "Unknown",
            "citations": [],
            "flags": ["Document not found"],
            "metadata" :{}
        })

def home(request):
    return render(request, 'home.html')

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            #preprocessing checks
            preprocessed_file = preprocess(uploaded_file)
            
            #if it's valid, save it
            if preprocessed_file["is_pdf"]:
                FileModel.objects.create(
                    title=form.cleaned_data['title'], 
                    file=uploaded_file
                )
                return render(request, 'success.html', {'num_pages': preprocessed_file["num_pages"]})

            #otheriwse throw error invalid pdf on upload page
            else: 
                return render(request, 'upload.html', {
                    'form': form, 
                    'errors': preprocessed_file.get("errors", ["Invalid PDF"])
                })


    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})



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
            doc_analysis = mock_classify_document(document_id) if document_id else None
            category = doc_analysis.get('category', [])
            prompt_sequence = []
            for cat in category:
                prompt_sequence.extend(prompt_library.get(cat, []))
            if "root" in prompt_library:
                prompt_sequence.insert(0, prompt_library["root"])
            prompt_sequence = list(dict.fromkeys(prompt_sequence)) #deduplicate
            
            # and context assembler
            external_context = mock_external_api(query)
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
                    'id': document_id,
                    'category': category,
                    "metadata": doc_analysis.get('metadata', {}),
                    "citations": doc_analysis.get('citations', []),
                    "flags": flags,
                },
                'external_context': external_context,
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
            original_data = mock_classify_document(document_id)
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
                'external_context': {},
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