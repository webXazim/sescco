from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_detail_localization_polish"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="slug",
            field=models.SlugField(max_length=255, unique=True),
        ),
    ]
