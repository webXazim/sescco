from django.db import migrations, models


INFO_EMAIL = "info@sescco.com"


def keep_info_email_only(apps, schema_editor):
    CompanyProfile = apps.get_model("core", "CompanyProfile")
    ContactMethod = apps.get_model("core", "ContactMethod")
    OfficeLocation = apps.get_model("core", "OfficeLocation")

    CompanyProfile.objects.update(
        email_primary=INFO_EMAIL,
        email_secondary="",
        email_third="",
    )
    OfficeLocation.objects.update(email=INFO_EMAIL)

    ContactMethod.objects.filter(url__istartswith="mailto:").update(
        is_active=False,
        show_on_contact_page=False,
        show_in_footer=False,
    )
    ContactMethod.objects.update_or_create(
        title="Email Us",
        defaults={
            "value": INFO_EMAIL,
            "icon_text": "✉",
            "url": f"mailto:{INFO_EMAIL}",
            "sort_order": 1,
            "is_active": True,
            "show_on_contact_page": True,
            "show_in_footer": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_footer_contact_location_social"),
    ]

    operations = [
        migrations.AlterField(
            model_name="companyprofile",
            name="email_secondary",
            field=models.EmailField(blank=True, default="", max_length=254),
        ),
        migrations.AlterField(
            model_name="companyprofile",
            name="email_third",
            field=models.EmailField(blank=True, default="", max_length=254),
        ),
        migrations.RunPython(keep_info_email_only, migrations.RunPython.noop),
    ]
