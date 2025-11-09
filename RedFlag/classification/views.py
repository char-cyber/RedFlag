

from django.shortcuts import render
from django.views.decorators.http import require_POST
from classification.services.pii_detection import detect_pii_pdf
from classification.services.classification_logic import classify_document
from django.http import JsonResponse
from pypdf import PdfReader

@require_POST
def classify_file_endpoint(request):
    """
    Accepts 'file_name': uploaded_file.name,
                'preprocessed_file': preprocessed_file
                'file'
    Renders template with classification, metadata, and PII flags.
    """
    uploaded_file = request.POST.get("file")
    if not uploaded_file:
        return JsonResponse({"error": "Missing file_id"}, status=400)

    #extract text and find PII flags                

    uploaded_file.seek(0) #starting at the start again
    text_content = ""
    try:
        # uploaded_file is a Django InMemoryUploadedFile or TemporaryUploadedFile
        pdf_reader = PdfReader(uploaded_file)
        for page in pdf_reader.pages:
            text_content += page.extract_text() or ""
            
        text_content = text_content.strip()

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


    pii_flags = detect_pii_pdf(uploaded_file)
    context = classify_document(text_content, pii_flags, preprocessed_file["num_pages"], preprocessed_file["num_images"])

    # # Build structured context
    # context = {
    #     'category': category,
    #     'metadata': {
    #         'pages': num_pages,
    #         'images': 0
    #     },
    #     'flags': [flag['text'] for flag in pii_flags],
    #     'citations': citations
    # }

    
    return JsonResponse(context, safe=True, json_dumps_params={'indent': 2})

