# Generated manually for SESCCO career module.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CareerPageSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("eyebrow", models.CharField(default="Careers", max_length=120)),
                ("hero_title", models.CharField(default="Build Your Career with SESCCO", max_length=255)),
                ("hero_subtitle", models.TextField(blank=True, default="Explore open positions, apply online and join a team committed to safe, reliable engineering execution.")),
                ("hero_image", models.ImageField(blank=True, null=True, upload_to="careers/page/")),
                ("intro_eyebrow", models.CharField(default="Open Opportunities", max_length=120)),
                ("intro_title", models.CharField(default="Find the right role for your next step", max_length=255)),
                ("intro_text", models.TextField(blank=True, default="We review every application carefully and invite shortlisted candidates for interview through official email.")),
                ("process_title", models.CharField(default="Simple hiring process", max_length=255)),
                ("process_text", models.TextField(blank=True, default="Apply, get reviewed, attend the interview and join the project team.")),
                ("show_filters", models.BooleanField(default=True)),
                ("show_process", models.BooleanField(default=True)),
                ("show_cta", models.BooleanField(default=True)),
                ("cta_title", models.CharField(default="Didn’t find the exact role?", max_length=255)),
                ("cta_text", models.TextField(blank=True, default="Check this page again soon or contact our HR team for future opportunities.")),
                ("cta_button_text", models.CharField(default="Contact HR", max_length=120)),
                ("cta_button_url", models.CharField(default="/contact/", max_length=255)),
            ],
            options={"verbose_name": "Career Page Settings", "verbose_name_plural": "Career Page Settings"},
        ),
        migrations.CreateModel(
            name="CareerDepartment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField(blank=True)),
            ],
            options={"verbose_name": "Career Department", "verbose_name_plural": "Career Departments", "ordering": ["sort_order", "id"]},
        ),
        migrations.CreateModel(
            name="JobOpening",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=180)),
                ("slug", models.SlugField(unique=True)),
                ("location", models.CharField(default="Dammam, Saudi Arabia", max_length=160)),
                ("employment_type", models.CharField(choices=[("full_time", "Full Time"), ("part_time", "Part Time"), ("contract", "Contract"), ("temporary", "Temporary"), ("internship", "Internship")], default="full_time", max_length=30)),
                ("work_mode", models.CharField(choices=[("site", "Site Based"), ("office", "Office Based"), ("hybrid", "Hybrid"), ("remote", "Remote")], default="site", max_length=30)),
                ("experience_level", models.CharField(blank=True, default="Experienced", max_length=120)),
                ("positions_available", models.PositiveIntegerField(default=1)),
                ("application_deadline", models.DateField(blank=True, null=True)),
                ("summary", models.TextField(help_text="Short card summary shown on the career listing page.")),
                ("responsibilities", models.TextField(blank=True, help_text="Use one line per responsibility.")),
                ("requirements", models.TextField(blank=True, help_text="Use one line per requirement.")),
                ("benefits", models.TextField(blank=True, help_text="Use one line per benefit or note.")),
                ("contact_email", models.EmailField(blank=True, help_text="Optional HR email for this role. Defaults to DEFAULT_FROM_EMAIL.", max_length=254)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("open", "Open"), ("closed", "Closed"), ("on_hold", "On Hold")], default="open", max_length=30)),
                ("is_featured", models.BooleanField(default=False)),
                ("department", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="jobs", to="careers.careerdepartment")),
            ],
            options={"verbose_name": "Job Opening", "verbose_name_plural": "Job Openings", "ordering": ["sort_order", "id"]},
        ),
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("full_name", models.CharField(max_length=140)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=60)),
                ("current_location", models.CharField(blank=True, max_length=160)),
                ("nationality", models.CharField(blank=True, max_length=120)),
                ("years_experience", models.DecimalField(blank=True, decimal_places=1, max_digits=4, null=True)),
                ("expected_salary", models.CharField(blank=True, max_length=120)),
                ("available_from", models.CharField(blank=True, max_length=120)),
                ("cover_letter", models.TextField(blank=True)),
                ("cv", models.FileField(help_text="Required CV / resume file.", upload_to="careers/applications/cv/%Y/%m/")),
                ("supporting_document", models.FileField(blank=True, null=True, upload_to="careers/applications/supporting/%Y/%m/")),
                ("certificate_document", models.FileField(blank=True, null=True, upload_to="careers/applications/certificates/%Y/%m/")),
                ("consent", models.BooleanField(default=False)),
                ("status", models.CharField(choices=[("received", "Received"), ("reviewing", "Reviewing"), ("shortlisted", "Shortlisted"), ("interview_invited", "Interview Invited"), ("rejected", "Rejected"), ("hired", "Hired")], default="received", max_length=30)),
                ("internal_notes", models.TextField(blank=True)),
                ("interview_date", models.DateTimeField(blank=True, null=True)),
                ("interview_mode", models.CharField(choices=[("in_person", "In Person"), ("online", "Online"), ("phone", "Phone Call")], default="in_person", max_length=30)),
                ("interview_location", models.CharField(blank=True, help_text="Office address, project site, phone number or meeting link.", max_length=255)),
                ("interview_notes", models.TextField(blank=True, help_text="Extra instructions for the applicant.")),
                ("invitation_sent_at", models.DateTimeField(blank=True, null=True)),
                ("job", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="applications", to="careers.jobopening")),
            ],
            options={"verbose_name": "Job Application", "verbose_name_plural": "Job Applications", "ordering": ["-created_at"]},
        ),
    ]
