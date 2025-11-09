# myapp/urls.py
from django.urls import path
from . import views
from .views import ContextQueryView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('upload/', views.upload_file, name='upload'),
    path('api/context-query/', ContextQueryView.as_view(), name='context-query'),
]

