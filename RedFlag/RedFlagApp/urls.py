from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='redflag_upload'),
    path('query/', views.ContextQueryView.as_view(), name='context_query'),
    path('feedback/', views.HITLFeedbackView.as_view(), name='hitl_feedback'),
]