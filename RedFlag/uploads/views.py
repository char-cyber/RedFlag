# myapp/views.py
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileModel # Assuming you have a model to store file info
from .utils import *

from django.http import JsonResponse

#classifcation
from classification.services.pii_detection import detect_pii_pdf
from classification.services.classification_logic import classify_document

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
                    return JsonResponse({"error": f"PDF text extraction failed: {e}"}, status=500)


                pii_flags = detect_pii_pdf(uploaded_file)
                context = classify_document(text_content, pii_flags, preprocessed_file["num_pages"], preprocessed_file["num_images"])

                return JsonResponse(context, safe = False)

            #otheriwse throw error invalid pdf on upload page
            else: 
                return JsonResponse({
                    "error": preprocessed_file.get("errors", ["Invalid PDF"])
                }, status=400)

        else:
            return JsonResponse({"error": form.errors}, status=400)
    form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


