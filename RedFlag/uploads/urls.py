# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
    path('analysis/', views.analysis, name='analysis'),
]

