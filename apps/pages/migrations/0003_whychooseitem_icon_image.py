# Generated manually for Upgrade 21 — why choose card image/text icons

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0002_homehighlight_icon_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="whychooseitem",
            name="icon_image",
            field=models.ImageField(
                blank=True,
                help_text="Optional square icon image. Recommended upload size: 96 x 96 px PNG/WebP/JPG. It renders as 32 x 32 px inside a 58 x 58 px badge.",
                null=True,
                upload_to="home/why-icons/",
            ),
        ),
        migrations.AlterField(
            model_name="whychooseitem",
            name="icon_text",
            field=models.CharField(
                blank=True,
                help_text="Fallback icon when no image is uploaded. Use one clean icon character such as ✓, ⚙, □, ✦, or an emoji. HTML is not required.",
                max_length=40,
            ),
        ),
    ]
