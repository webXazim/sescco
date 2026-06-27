# Generated for upgrade 163: Certifications & clients public page cleanup.
from django.db import migrations, models


def update_existing_trust_settings(apps, schema_editor):
    TrustPageSettings = apps.get_model('clients', 'TrustPageSettings')
    TrustPageSettings.objects.update(
        eyebrow='Certifications & Clients',
        hero_title='Certifications and clients.',
        hero_subtitle='Review SESCCO certificates first, then the client organizations connected to our project experience.',
        partners_eyebrow='Project Network',
        partners_title='Project contractors only for project detail records.',
        show_partners=False,
        show_certificates=True,
        show_clients=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0002_certificate_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='partner',
            options={'ordering': ['sort_order', 'id'], 'verbose_name': 'Project contractor', 'verbose_name_plural': 'Project contractors'},
        ),
        migrations.AlterField(
            model_name='trustpagesettings',
            name='eyebrow',
            field=models.CharField(default='Certifications & Clients', max_length=120),
        ),
        migrations.AlterField(
            model_name='trustpagesettings',
            name='hero_title',
            field=models.CharField(default='Certifications and clients.', max_length=255),
        ),
        migrations.AlterField(
            model_name='trustpagesettings',
            name='hero_subtitle',
            field=models.TextField(blank=True, default='Review SESCCO certificates first, then the client organizations connected to our project experience.'),
        ),
        migrations.AlterField(
            model_name='trustpagesettings',
            name='partners_title',
            field=models.CharField(default='Project contractors only for project detail records.', max_length=255),
        ),
        migrations.AlterField(
            model_name='trustpagesettings',
            name='show_partners',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(update_existing_trust_settings, migrations.RunPython.noop),
    ]
