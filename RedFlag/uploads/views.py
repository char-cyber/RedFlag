# myapp/views.py
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileModel # Assuming you have a model to store file info
from .utils import *

import json

#classifcation
from classification.services.pii_detection import detect_pii_pdf, detect_pii_docx
from classification.services.classification_logic import classify_document



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
                    classification = classify_document(text_content, pii_flags, preprocessed_file["num_pages"], preprocessed_file["num_images"], preprocessed_file["images"])
 

                else: #docx processing
                    text, images = extract_docx_content(uploaded_file)
                    preprocessed_file["num_images"] = len(images)
                    
                    pii_flags = detect_pii_docx(text, images)
                    classification = classify_document(text, pii_flags, preprocessed_file["num_pages"], preprocessed_file["num_images"], images)


                # <!-- variables needed -->

                #  - doc_name
                #  - category
                #  - confidence
                #  - num_pages
                #  - num images
                #  - num_flags
                #  - flag_info: critical, name, page, line, description

                return render(request, 'analysis.html', {
                    'doc_name' : form.cleaned_data['title'],
                    'category': classification["category"],
                    'confidence': classification["confidence"],
                    'num_pages': preprocessed_file["num_pages"],
                    'num images': preprocessed_file["num_images"],
                    'num_flags': classification["num_flags"],
                    'flag_info': classification["flag_info"]
                })

                # return render (request, 'success.html', {'classification' : classification})
            


            #otheriwse throw error invalid pdf on upload page
            else: 
                return render(request, 'upload.html', {
                    'form': form, 
                    'errors': preprocessed_file.get("errors", ["Invalid PDF"])
                })


    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})


def analysis(request):
    return render(request, 'analysis.html')

