from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inquiries", "0002_contact_page_map_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="contactpagesettings",
            name="notification_email",
            field=models.EmailField(
                blank=True,
                default="info@sescco.com",
                help_text="Default email address that receives contact form submissions. Subject-specific email_to overrides this when set.",
                max_length=254,
            ),
        ),
        migrations.AddField(
            model_name="contactpagesettings",
            name="email_from_name",
            field=models.CharField(blank=True, default="SESCCO Website", max_length=120),
        ),
    ]
