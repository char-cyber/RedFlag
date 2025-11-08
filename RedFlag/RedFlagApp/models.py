from django.db import models

class MyFileModel(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/') # 'uploads/' is a subdirectory within MEDIA_ROOT
    uploaded_at = models.DateTimeField(auto_now_add=True)
