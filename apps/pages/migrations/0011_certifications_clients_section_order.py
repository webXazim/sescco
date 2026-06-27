# Generated for upgrade 163: put certificates before clients and retire public partner section.
from django.db import migrations


def update_clients_certifications_order(apps, schema_editor):
    PageSectionOrder = apps.get_model('pages', 'PageSectionOrder')
    canonical = [
        ('hero', 'Hero', 'Certifications and clients hero', 10, True),
        ('metrics', 'Trust metrics', 'Vendor codes and trust metrics', 15, True),
        ('certificates', 'Certificates', 'Certificate image grid and modal', 20, True),
        ('clients', 'Clients', 'Client logo grid and filters', 30, True),
        ('accreditations', 'Accreditations', 'Accreditation references', 40, True),
        ('standards', 'Compliance standards', 'Compliance and standards cards', 50, True),
        ('testimonials', 'Testimonials', 'Client testimonials', 60, True),
        ('documents', 'Documents', 'Supporting documents', 70, True),
        ('partners', 'Project contractors', 'Contractor records are used for project details only, not this public page.', 900, False),
    ]
    for section_key, label, description, order, active in canonical:
        PageSectionOrder.objects.update_or_create(
            page_key='clients_certifications',
            section_key=section_key,
            defaults={
                'page_label': 'Certifications & clients page',
                'section_label': label,
                'description': description,
                'sort_order': order,
                'is_active': active,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('pages', '0010_home_certificates_limit_default_six'),
    ]

    operations = [
        migrations.RunPython(update_clients_certifications_order, migrations.RunPython.noop),
    ]
