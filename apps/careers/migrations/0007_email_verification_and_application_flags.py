# Generated for SESCCO career email verification upgrade
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("careers", "0006_career_production_hardening"),
    ]

    operations = [
        migrations.AddField(
            model_name="careerpagesettings",
            name="email_verification_subject",
            field=models.CharField(default="Verify your SESCCO career application email", max_length=255),
        ),
        migrations.AddField(
            model_name="careerpagesettings",
            name="email_verification_body",
            field=models.TextField(default="Dear applicant,\n\nUse this verification code to continue your SESCCO job application:\n\n{{ code }}\n\nPosition: {{ job.title }}\nThis code will expire in {{ expiry_minutes }} minutes.\n\nIf you did not request this code, please ignore this email.\n\nRegards,\nSESCCO HR Team\n"),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="email_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="email_verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="CareerEmailVerification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("email", models.EmailField(db_index=True, max_length=254)),
                ("code_hash", models.CharField(max_length=128)),
                ("expires_at", models.DateTimeField(db_index=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("send_count", models.PositiveIntegerField(default=1)),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("sent_ip", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True, default="")),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="email_verifications", to="careers.jobopening")),
            ],
            options={
                "verbose_name": "Career Email Verification",
                "verbose_name_plural": "Career Email Verifications",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="careeremailverification",
            index=models.Index(fields=["job", "email", "expires_at"], name="careers_emai_job_id_56c57d_idx"),
        ),
        migrations.AddIndex(
            model_name="careeremailverification",
            index=models.Index(fields=["verified_at", "used_at"], name="careers_emai_verifie_f04b16_idx"),
        ),
    ]
