# Generated for SESCCO contact page map settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inquiries", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactpagesettings",
            name="map_eyebrow",
            field=models.CharField(default="Find Us", max_length=120),
        ),
        migrations.AddField(
            model_name="contactpagesettings",
            name="map_title",
            field=models.CharField(default="Visit our office location.", max_length=255),
        ),
        migrations.AddField(
            model_name="contactpagesettings",
            name="map_subtitle",
            field=models.TextField(blank=True, default="Use the map below to view SESCCO’s office location and open directions in Google Maps."),
        ),
        migrations.AddField(
            model_name="contactpagesettings",
            name="google_map_embed_url",
            field=models.URLField(blank=True, help_text="Paste a Google Maps embed URL. Example: https://www.google.com/maps?q=Dammam%2C%20Saudi%20Arabia&output=embed", max_length=1000),
        ),
        migrations.AddField(
            model_name="contactpagesettings",
            name="google_map_url",
            field=models.URLField(blank=True, help_text="Paste the public Google Maps location/directions URL used by the Get Directions button.", max_length=1000),
        ),
        migrations.AddField(
            model_name="contactpagesettings",
            name="map_button_text",
            field=models.CharField(default="Open in Google Maps", max_length=120),
        ),
    ]
