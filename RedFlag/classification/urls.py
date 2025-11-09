from django.urls import path, include
from . import views

urlpatterns = [
    path('api/classify/', views.classify_file_endpoint, name='classify'),
]
