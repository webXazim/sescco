# Generated manually for Upgrade 18 — trust metric icon upload guidance

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_trustmetric_icon_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trustmetric",
            name="icon_image",
            field=models.ImageField(
                blank=True,
                help_text=(
                    "Optional square icon image. Recommended upload size: 96 x 96 px "
                    "PNG/WebP/JPG. It renders as 32 x 32 px inside the premium "
                    "64 x 64 px metric badge."
                ),
                null=True,
                upload_to="trust/metric-icons/",
            ),
        ),
    ]
