# Generated for upgrade 158: home certificate preview limit default.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_homehero_show_sphere'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homesectionsettings',
            name='certificates_limit',
            field=models.PositiveIntegerField(default=6),
        ),
    ]
