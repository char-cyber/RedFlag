# myapp/views.py
from django.shortcuts import render
from .forms import UploadFileForm
from .models import FileModel # Assuming you have a model to store file info

def home(request):
    return render(request, 'home.html')

def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            FileModel.objects.create(title=form.cleaned_data['title'], file=uploaded_file)
            return render(request, 'success.html')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})