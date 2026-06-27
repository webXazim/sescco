from django.urls import path
from . import views

urlpatterns = [
    path("", views.downloads, name="downloads"),
    path("request/", views.document_request, name="document_request"),
    path("<slug:slug>/download/", views.download_file, name="download_file"),
]
