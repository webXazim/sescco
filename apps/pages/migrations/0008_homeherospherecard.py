# Generated for Upgrade 103 — Home hero sphere cards CMS

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0007_prune_removed_downloads_section_order"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomeHeroSphereCard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("title", models.CharField(help_text="Main label shown on image cards and used for accessibility.", max_length=120)),
                ("subtitle", models.CharField(blank=True, help_text="Short supporting text shown on the card.", max_length=180)),
                ("card_type", models.CharField(choices=[("image", "Image card"), ("data", "Data / text card")], default="image", max_length=20)),
                ("big_text", models.CharField(blank=True, help_text="Large text for data cards, such as QA, KSA, 2015, SEC.", max_length=40)),
                ("image", models.ImageField(blank=True, help_text="Upload card image for image cards. Recommended ratio: 3:4, at least 600 x 800 px. PNG/WebP/JPG.", null=True, upload_to="home/sphere-cards/")),
                ("static_image_path", models.CharField(blank=True, help_text='Optional fallback static path, for example: "img/hero_sphere/project-01.svg". Uploaded image takes priority.', max_length=255)),
                ("alt_text", models.CharField(blank=True, max_length=160)),
                ("is_featured", models.BooleanField(default=True, help_text="Featured cards are loaded into the home hero sphere. Keep 12–18 active cards for best shape.")),
            ],
            options={
                "verbose_name": "Home Hero Sphere Card",
                "verbose_name_plural": "Home Hero Sphere Cards",
                "ordering": ["sort_order", "id"],
            },
        ),
    ]
