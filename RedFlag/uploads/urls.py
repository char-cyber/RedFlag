# myapp/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload'),
    path('classification/', include('classification.urls')),
]

