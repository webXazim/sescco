# Generated manually for Upgrade 32 — home highlight image/text icons

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="homehighlight",
            name="icon_image",
            field=models.ImageField(
                blank=True,
                help_text="Optional square icon image. Recommended upload size: 96 x 96 px PNG/WebP/JPG. It renders as 42 x 42 px inside a 72 x 72 px badge.",
                null=True,
                upload_to="home/highlight-icons/",
            ),
        ),
        migrations.AlterField(
            model_name="homehighlight",
            name="icon_text",
            field=models.CharField(
                blank=True,
                help_text="Fallback icon when no image is uploaded. Use one clean icon character such as ✓, ⚙, □, ✦, or an emoji. HTML is not required.",
                max_length=40,
            ),
        ),
    ]
