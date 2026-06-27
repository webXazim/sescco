# Generated for Upgrade 107 — Home hero sphere settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0008_homeherospherecard"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeHeroSphereConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_enabled", models.BooleanField(default=True, help_text="Turn the animated home hero sphere on or off.")),
                ("hide_on_mobile", models.BooleanField(default=True, help_text="Recommended: keep enabled so mobile hero does not break.")),
                ("alignment", models.CharField(choices=[("default", "Default current design"), ("soft", "Softer background feel")], default="default", help_text="Default keeps the current approved visual design. Soft only reduces opacity slightly.", max_length=20)),
                ("desktop_size", models.PositiveIntegerField(default=100, help_text="Optional tuning only. 100 keeps the approved design size.")),
            ],
            options={
                "verbose_name": "Home Hero Sphere Settings",
                "verbose_name_plural": "Home Hero Sphere Settings",
            },
        ),
    ]
