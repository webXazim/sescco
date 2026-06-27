from django.urls import path
from . import views

urlpatterns = [
    path("", views.career_list, name="career_list"),
    path("<slug:slug>/", views.job_detail, name="job_detail"),
    path("<slug:slug>/apply/", views.apply_job, name="job_apply"),
    path("<slug:slug>/apply/check-email/", views.check_application_email, name="job_apply_check_email"),
    path("<slug:slug>/apply/send-code/", views.send_application_email_code, name="job_apply_send_code"),
    path("<slug:slug>/apply/verify-code/", views.verify_application_email_code, name="job_apply_verify_code"),
    path("<slug:slug>/success/", views.application_success, name="career_application_success"),
]
