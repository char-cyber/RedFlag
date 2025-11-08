from django.db import models

class FileModel(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='') # uatomatically to media
    uploaded_at = models.DateTimeField(auto_now_add=True)

    #for outputting a string
    def __str__(self):
        return self.title
