from django.urls import path
from .views import uploadedFile

urlpatterns = [
    path('',uploadedFile,name='file-upload'),
]