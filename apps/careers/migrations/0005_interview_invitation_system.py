# Manual migration for Careers Upgrade 6: Interview Invitation System

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import apps.careers.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("careers", "0004_applicant_system"),
    ]

    operations = [
        migrations.AddField(
            model_name="careerpagesettings",
            name="email_from_name",
            field=models.CharField(blank=True, default="SESCCO HR Team", max_length=140),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="interview_email_subject",
            field=models.CharField(default=apps.careers.models.DEFAULT_INTERVIEW_EMAIL_SUBJECT, max_length=255),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="interview_email_body",
            field=models.TextField(default=apps.careers.models.DEFAULT_INTERVIEW_EMAIL_BODY),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="rejection_email_subject",
            field=models.CharField(default=apps.careers.models.DEFAULT_REJECTION_EMAIL_SUBJECT, max_length=255),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="rejection_email_body",
            field=models.TextField(default=apps.careers.models.DEFAULT_REJECTION_EMAIL_BODY),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="rejection_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="JobApplicationEmailLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email_type", models.CharField(choices=[("interview_invitation", "Interview Invitation"), ("rejection", "Rejection Email"), ("custom", "Custom Email")], default="custom", max_length=40)),
                ("recipient", models.EmailField(max_length=254)),
                ("subject", models.CharField(max_length=255)),
                ("body", models.TextField()),
                ("success", models.BooleanField(default=True)),
                ("error_message", models.TextField(blank=True, default="")),
                ("interview_date", models.DateTimeField(blank=True, null=True)),
                ("interview_mode", models.CharField(blank=True, default="", max_length=30)),
                ("interview_location", models.CharField(blank=True, default="", max_length=255)),
                ("application", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="email_logs", to="careers.jobapplication")),
                ("sent_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "Application Email Log",
                "verbose_name_plural": "Application Email Logs",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="jobapplicationemaillog",
            index=models.Index(fields=["email_type", "created_at"], name="careers_app_email_t_44b4bb_idx"),
        ),
        migrations.AddIndex(
            model_name="jobapplicationemaillog",
            index=models.Index(fields=["success", "created_at"], name="careers_app_success_7b43b9_idx"),
        ),
    ]
