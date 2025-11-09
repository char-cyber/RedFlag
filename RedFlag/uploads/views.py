# myapp/views.py
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileModel # Assuming you have a model to store file info
from .utils import *

import json

#classifcation
from classification.services.pii_detection import detect_pii_pdf
from classification.services.classification_logic import classify_document


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
            if preprocessed_file["is_pdf"] or preprocessed_file["is_docx"]:
                FileModel.objects.create(
                    title=form.cleaned_data['title'], 
                    file=uploaded_file
                )


                #extract text and find PII flags                

                uploaded_file.seek(0) #starting at the start again
                text_content = ""
                if preprocessed_file["is_pdf"]:
                    try:
                        # uploaded_file is a Django InMemoryUploadedFile or TemporaryUploadedFile
                        pdf_reader = PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            text_content += page.extract_text() or ""
                            
                        text_content = text_content.strip()

                    except Exception as e:
                        return render(request, 'upload.html', {
                            'form': form, 
                            'errors': e
                        })  

                    pii_flags = detect_pii_pdf(uploaded_file)
                    category = classify_document(text_content, pii_flags)
                else:
                    text, images = extract_docx_content(uploaded_file)
                    
                    pii_flags = detect_pii_docx(text, images)
                    category = classify_document(text, pii_flags)

                return render(request, 'success.html', {
                    'num_pages': preprocessed_file["num_pages"], 
                    'num_images': preprocessed_file["num_images"],
                    'pii_flags': pii_flags,
                    'category': category
                    })

            #otheriwse throw error invalid pdf on upload page
            else: 
                return render(request, 'upload.html', {
                    'form': form, 
                    'errors': preprocessed_file.get("errors", ["Invalid PDF"])
                })


    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

