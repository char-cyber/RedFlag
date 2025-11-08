# myapp/views.py
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileModel # Assuming you have a model to store file info
from .utils import *

#classifcation
from classification.services.pii_detection import detect_pii


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
                #extract text for classification
                uploaded_file.seek(0) #starting at the start again
                text_content = extract_text_from_file(uploaded_file)

                pii_flags = detect_pii(text_content)

                return render(request, 'success.html', {
                    'num_pages': preprocessed_file["num_pages"], 
                    'num_images': preprocessed_file["num_images"],
                    'pii_flags': pii_flags
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

