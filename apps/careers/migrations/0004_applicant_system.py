# Manual migration for Careers Upgrade 4: Applicant System

import django.db.models.deletion
import apps.careers.models
from django.db import migrations, models
from django.utils import timezone


def normalize_statuses_and_references(apps, schema_editor):
    JobApplication = apps.get_model("careers", "JobApplication")
    for application in JobApplication.objects.all():
        if application.status == "received":
            application.status = "new"
        elif application.status == "reviewing":
            application.status = "reviewed"
        if application.email:
            application.email = application.email.strip().lower()
        if not application.application_reference:
            stamp = timezone.now().strftime("%Y%m")
            application.application_reference = f"SES-{stamp}-{application.pk:06d}"
        if not application.status_updated_at:
            application.status_updated_at = application.created_at or timezone.now()
        application.save(update_fields=["status", "email", "application_reference", "status_updated_at", "updated_at"])


def reverse_statuses(apps, schema_editor):
    JobApplication = apps.get_model("careers", "JobApplication")
    JobApplication.objects.filter(status="new").update(status="received")
    JobApplication.objects.filter(status="reviewed").update(status="reviewing")


class Migration(migrations.Migration):

    dependencies = [
        ("careers", "0003_job_posting_cms"),
    ]

    operations = [
        migrations.AddField(
            model_name="careerpagesettings",
            name="applicant_profile_title",
            field=models.CharField(default="Applicant profile", max_length=180),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="applicant_profile_text",
            field=models.TextField(blank=True, default="Add your location, work authorization, experience and useful profile links so HR can review the application faster."),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="document_upload_title",
            field=models.CharField(default="Application documents", max_length=180),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="document_upload_text",
            field=models.TextField(blank=True, default="Upload your CV and any supporting certificates, licenses or project documents. Multiple additional documents are supported."),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="duplicate_application_title",
            field=models.CharField(default="Application already submitted", max_length=180),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="duplicate_application_text",
            field=models.TextField(blank=True, default="This email has already been used to apply for this job. Please contact HR if you need to update your application."),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="privacy_notice",
            field=models.TextField(blank=True, default="Your information will only be used for recruitment review and official communication about this application."),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="application_reference",
            field=models.CharField(blank=True, editable=False, max_length=40),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="alternate_email",
            field=models.EmailField(blank=True, default="", max_length=254),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="work_authorization",
            field=models.CharField(blank=True, choices=[("", "Not specified"), ("saudi_national", "Saudi National"), ("transferable_iqama", "Transferable Iqama"), ("company_sponsorship", "Requires Company Sponsorship"), ("visit_or_temporary", "Visit / Temporary Visa"), ("other", "Other")], default="", max_length=40),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="preferred_interview_time",
            field=models.CharField(blank=True, default="", max_length=160),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="linkedin_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="portfolio_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="source",
            field=models.CharField(blank=True, choices=[("", "Not specified"), ("website", "Company Website"), ("linkedin", "LinkedIn"), ("referral", "Employee Referral"), ("job_board", "Job Board"), ("walk_in", "Walk-in"), ("other", "Other")], default="website", max_length=40),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="status_updated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="shortlisted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="rejected_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="hired_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="submitted_ip",
            field=models.GenericIPAddressField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="user_agent",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.RunPython(normalize_statuses_and_references, reverse_statuses),
        migrations.AlterField(
            model_name="jobapplication",
            name="application_reference",
            field=models.CharField(blank=True, editable=False, max_length=40, unique=True),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="status",
            field=models.CharField(choices=[("new", "New"), ("reviewed", "Reviewed"), ("shortlisted", "Shortlisted"), ("interview_invited", "Interview Invited"), ("rejected", "Rejected"), ("hired", "Hired")], default="new", max_length=30),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="cv",
            field=models.FileField(help_text="Required CV / resume file.", upload_to=apps.careers.models.application_file_path),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="supporting_document",
            field=models.FileField(blank=True, null=True, upload_to=apps.careers.models.application_file_path),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="certificate_document",
            field=models.FileField(blank=True, null=True, upload_to=apps.careers.models.application_file_path),
        ),
        migrations.CreateModel(
            name="JobApplicationDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("document_type", models.CharField(choices=[("supporting", "Supporting Document"), ("certificate", "Certificate / License"), ("portfolio", "Portfolio / Project Evidence"), ("id", "ID / Iqama Copy"), ("other", "Other")], default="supporting", max_length=30)),
                ("title", models.CharField(blank=True, default="", max_length=180)),
                ("file", models.FileField(upload_to=apps.careers.models.application_extra_document_path)),
                ("notes", models.TextField(blank=True, default="")),
                ("uploaded_by_applicant", models.BooleanField(default=True)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="careers.jobapplication")),
            ],
            options={"verbose_name": "Application Document", "verbose_name_plural": "Application Documents", "ordering": ["document_type", "id"]},
        ),
        migrations.AddIndex(
            model_name="jobapplication",
            index=models.Index(fields=["job", "email"], name="careers_app_job_80b560_idx"),
        ),
        migrations.AddIndex(
            model_name="jobapplication",
            index=models.Index(fields=["status", "created_at"], name="careers_app_status_8fb3d8_idx"),
        ),
    ]
