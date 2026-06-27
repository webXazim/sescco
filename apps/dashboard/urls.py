from django.urls import path
from . import views

urlpatterns = [
    path("careers/applications/<int:pk>/download/<str:field_name>/", views.career_application_field_download, name="career_application_field_download"),
    path("careers/applications/<int:pk>/documents/<int:document_pk>/download/", views.career_application_document_download, name="career_application_document_download"),
    path("careers/applications/<int:pk>/", views.career_application_detail, name="career_application_detail"),
    path("careers/applications/", views.career_applications_dashboard, name="career_applications_dashboard"),
    path("translations/", views.translation_dashboard, name="translation_dashboard"),
    path("", views.dashboard_home, name="dashboard_home"),
]
