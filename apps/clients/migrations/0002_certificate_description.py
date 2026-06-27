# Generated for certificate image grid modal upgrade.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='certificate',
            name='description',
            field=models.TextField(blank=True, default='', help_text='Short public description shown in the certificate modal.'),
        ),
    ]
