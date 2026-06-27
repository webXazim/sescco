from django.urls import path
from . import views

urlpatterns = [
    path("healthz/", views.healthz, name="healthz"),
    path("localized-sitemap.xml", views.localized_sitemap, name="localized_sitemap"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
