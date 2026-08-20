from django.db import migrations


ADDRESS = "C3FW+Q7V Dammam 6619, King Fahd Road, Office - 05, Dammam - 32243 - 3404, KSA"
MAP_EMBED_URL = "https://www.google.com/maps?q=C3FW%2BQ7V%20Dammam%206619%2C%20King%20Fahd%20Road%2C%20Office%2005%2C%20Dammam%2032243-3404%2C%20Saudi%20Arabia&output=embed"
MAP_URL = "https://www.google.com/maps/search/?api=1&query=C3FW%2BQ7V%20Dammam%206619%2C%20King%20Fahd%20Road%2C%20Office%2005%2C%20Dammam%2032243-3404%2C%20Saudi%20Arabia"


def apply_footer_contact_details(apps, schema_editor):
    CompanyProfile = apps.get_model("core", "CompanyProfile")
    ContactMethod = apps.get_model("core", "ContactMethod")
    OfficeLocation = apps.get_model("core", "OfficeLocation")
    SocialLink = apps.get_model("core", "SocialLink")
    ContactPageSettings = apps.get_model("inquiries", "ContactPageSettings")

    company = CompanyProfile.objects.first() or CompanyProfile()
    company.email_primary = "info@sescco.com"
    company.email_secondary = "mm.ruhit@sescco.com"
    company.email_third = "mehrab@sescco.com"
    company.address = ADDRESS
    company.city = "Dammam"
    company.country = "Saudi Arabia"
    company.phone_primary = ""
    company.phone_secondary = ""
    company.save()

    office = OfficeLocation.objects.filter(is_primary=True).first() or OfficeLocation.objects.first()
    if office is None:
        office = OfficeLocation(name="Head Office")
    office.address = ADDRESS
    office.city = "Dammam"
    office.country = "Saudi Arabia"
    office.email = "info@sescco.com"
    office.phone = ""
    office.map_url = MAP_URL
    office.map_embed_url = MAP_EMBED_URL
    office.is_primary = True
    office.is_active = True
    office.save()

    contact_settings = ContactPageSettings.objects.first() or ContactPageSettings()
    contact_settings.google_map_embed_url = MAP_EMBED_URL
    contact_settings.google_map_url = MAP_URL
    contact_settings.map_title = "Visit our Dammam office."
    contact_settings.map_subtitle = ADDRESS
    contact_settings.show_map = True
    contact_settings.save()

    ContactMethod.objects.exclude(url__startswith="mailto:").update(
        is_active=False,
        show_on_contact_page=False,
        show_in_footer=False,
    )
    ContactMethod.objects.filter(title="Email Us").update(
        is_active=False,
        show_on_contact_page=False,
        show_in_footer=False,
    )
    for index, (title, email) in enumerate((
        ("General Email", "info@sescco.com"),
        ("Management Email", "mm.ruhit@sescco.com"),
        ("Projects Email", "mehrab@sescco.com"),
    ), start=1):
        ContactMethod.objects.update_or_create(
            title=title,
            defaults={
                "value": email,
                "icon_text": "✉",
                "url": f"mailto:{email}",
                "sort_order": index,
                "is_active": True,
                "show_on_contact_page": True,
                "show_in_footer": True,
            },
        )

    for title, url, icon_text, sort_order in (
        ("LinkedIn", "https://www.linkedin.com/in/summit-engineering-solutions-contracting-company-sescco-8b08113a0", "in", 1),
        ("Facebook", "https://www.facebook.com/profile.php?id=61593735353212", "f", 2),
    ):
        SocialLink.objects.update_or_create(
            title=title,
            defaults={"url": url, "icon_text": icon_text, "sort_order": sort_order, "is_active": True},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_production_client_request_cleanup"),
        ("inquiries", "0003_contact_email_notifications"),
    ]

    operations = [
        migrations.RunPython(apply_footer_contact_details, migrations.RunPython.noop),
    ]
