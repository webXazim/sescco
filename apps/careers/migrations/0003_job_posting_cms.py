# Manual migration for Careers Upgrade 2: Job Posting CMS

from django.db import migrations, models


def move_legacy_open_jobs_to_published(apps, schema_editor):
    JobOpening = apps.get_model("careers", "JobOpening")
    JobOpening.objects.filter(status="open").update(status="published")


def restore_legacy_open_jobs(apps, schema_editor):
    JobOpening = apps.get_model("careers", "JobOpening")
    JobOpening.objects.filter(status="published").update(status="open")


class Migration(migrations.Migration):

    dependencies = [
        ("careers", "0002_careerbenefit_careerprocessstep_careerstat_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobopening",
            name="job_code",
            field=models.CharField(blank=True, default="", help_text="Optional internal reference, for example SES-ENG-001.", max_length=40),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="job_level",
            field=models.CharField(choices=[("entry", "Entry Level"), ("junior", "Junior"), ("mid", "Mid Level"), ("senior", "Senior"), ("lead", "Lead / Supervisor"), ("manager", "Manager")], default="mid", max_length=30),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="job_description",
            field=models.TextField(blank=True, default="", help_text="Full description shown on the job detail page."),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="qualifications",
            field=models.TextField(blank=True, default="", help_text="Use one line per qualification, certificate or education requirement."),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="skills",
            field=models.TextField(blank=True, default="", help_text="Use one line per preferred skill."),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="salary_range",
            field=models.CharField(blank=True, default="", help_text="Optional salary range, for example SAR 5,000 - 7,000.", max_length=120),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="salary_note",
            field=models.CharField(blank=True, default="", help_text="Optional note, for example Depends on experience.", max_length=180),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="show_salary",
            field=models.BooleanField(default=False, help_text="Turn on only when salary information should be public."),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="apply_button_text",
            field=models.CharField(default="Apply Now", max_length=120),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="external_application_url",
            field=models.URLField(blank=True, default="", help_text="Optional external apply link. Leave blank to use the built-in application form."),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="published_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="seo_title",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="jobopening",
            name="seo_description",
            field=models.CharField(blank=True, default="", max_length=320),
        ),
        migrations.RunPython(move_legacy_open_jobs_to_published, restore_legacy_open_jobs),
        migrations.AlterField(
            model_name="jobopening",
            name="employment_type",
            field=models.CharField(choices=[("full_time", "Full-time"), ("part_time", "Part-time"), ("contract", "Contract"), ("temporary", "Temporary"), ("internship", "Internship")], default="full_time", max_length=30),
        ),
        migrations.AlterField(
            model_name="jobopening",
            name="status",
            field=models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("on_hold", "On Hold"), ("closed", "Closed")], default="published", max_length=30),
        ),
        migrations.AddIndex(
            model_name="jobopening",
            index=models.Index(fields=["status", "is_active", "application_deadline"], name="careers_job_status_f56d0a_idx"),
        ),
        migrations.AddIndex(
            model_name="jobopening",
            index=models.Index(fields=["is_featured", "sort_order"], name="careers_job_feature_2d8a52_idx"),
        ),
    ]
