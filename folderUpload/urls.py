from django.urls import path
from .views import *

urlpatterns = [
    path('',uploadedFile,name='file-upload'),
]