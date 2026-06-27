from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("pages/<slug:slug>/", views.generic_page, name="generic_page"),
]
