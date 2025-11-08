from django.db import models
from utils import count_pages

class FileModel(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='') # uatomatically to media
    uploaded_at = models.DateTimeField(auto_now_add=True)

    #for outputting a string
    def __str__(self):
        return self.title
    
    def page_count(self):
        return count_pages(self.file)
