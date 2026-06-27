# Generated manually for Upgrade 32 — trust metric image/text icons

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="trustmetric",
            name="icon_image",
            field=models.ImageField(
                blank=True,
                help_text="Optional square icon image. Recommended upload size: 96 x 96 px PNG/WebP/JPG. It renders as 24 x 24 px inside the circular metric icon.",
                null=True,
                upload_to="trust/metric-icons/",
            ),
        ),
        migrations.AlterField(
            model_name="trustmetric",
            name="icon_text",
            field=models.CharField(
                blank=True,
                help_text="Fallback icon when no image is uploaded. Use one clean icon character such as ✓, 🛡, ✦, or an emoji. HTML is not required.",
                max_length=40,
            ),
        ),
    ]
