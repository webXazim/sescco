from django.db import migrations


PLUS_CODE = "C3FW+Q7V"
DISPLAY_LOCATION = "C3FW+Q7V, Dammam, Saudi Arabia"
MAP_URL = "https://maps.app.goo.gl/QD8iU89NpRodzpeA9"
MAP_EMBED_URL = "https://www.google.com/maps?q=26.4244875%2C50.0956719&z=17&output=embed"


def apply_exact_google_maps_location(apps, schema_editor):
    CompanyProfile = apps.get_model("core", "CompanyProfile")
    OfficeLocation = apps.get_model("core", "OfficeLocation")
    ContactPageSettings = apps.get_model("inquiries", "ContactPageSettings")

    CompanyProfile.objects.update(
        address=DISPLAY_LOCATION,
        city="Dammam",
        country="Saudi Arabia",
        map_embed_url=MAP_EMBED_URL,
    )

    office = OfficeLocation.objects.filter(is_primary=True).first() or OfficeLocation.objects.first()
    if office is None:
        office = OfficeLocation(name="Main Office")
    office.address = PLUS_CODE
    office.city = "Dammam"
    office.country = "Saudi Arabia"
    office.map_url = MAP_URL
    office.map_embed_url = MAP_EMBED_URL
    office.is_primary = True
    office.is_active = True
    office.save()

    contact_settings = ContactPageSettings.objects.first() or ContactPageSettings()
    contact_settings.google_map_embed_url = MAP_EMBED_URL
    contact_settings.google_map_url = MAP_URL
    contact_settings.map_title = "Visit our Dammam office."
    contact_settings.map_subtitle = DISPLAY_LOCATION
    contact_settings.show_map = True
    contact_settings.save()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0012_info_email_only"),
        ("inquiries", "0003_contact_email_notifications"),
    ]

    operations = [
        migrations.RunPython(apply_exact_google_maps_location, migrations.RunPython.noop),
    ]
