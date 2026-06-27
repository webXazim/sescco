# Generated for Upgrade 110 — Admin toggle for home hero sphere

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0008_homeherospherecard"),
    ]

    operations = [
        migrations.AddField(
            model_name="homehero",
            name="show_sphere",
            field=models.BooleanField(
                default=True,
                help_text="Turn the animated/service-card sphere on or off in the home page hero.",
            ),
        ),
    ]
