# myapp/views.py
from django.shortcuts import render
from .forms import UploadFileForm
from .models import MyFileModel # Assuming you have a model to store file info

def upload_file_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the file here
            uploaded_file = request.FILES['file']
            # Example: Save to a model
            MyFileModel.objects.create(title=form.cleaned_data['title'], file=uploaded_file)
            return render(request, 'success.html')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})