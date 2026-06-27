from django.db import migrations


def prune_removed_downloads_section_order(apps, schema_editor):
    PageSectionOrder = apps.get_model("pages", "PageSectionOrder")
    PageSectionOrder.objects.filter(page_key="downloads").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0006_page_section_order_proxy_admins"),
    ]

    operations = [
        migrations.RunPython(prune_removed_downloads_section_order, migrations.RunPython.noop),
    ]
