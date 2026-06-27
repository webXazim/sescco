from django.urls import path
from . import views

urlpatterns = [
    path("", views.clients_certifications, name="clients_certifications"),
]
