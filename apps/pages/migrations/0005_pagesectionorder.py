from django.db import migrations, models


def seed_section_order(apps, schema_editor):
    PageSectionOrder = apps.get_model("pages", "PageSectionOrder")
    from apps.pages.section_registry import iter_default_sections

    for section in iter_default_sections():
        PageSectionOrder.objects.get_or_create(
            page_key=section["page_key"],
            section_key=section["section_key"],
            defaults={
                "page_label": section["page_label"],
                "section_label": section["section_label"],
                "description": section["description"],
                "sort_order": section["sort_order"],
                "is_active": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0004_leadershipmessage_background_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageSectionOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("page_key", models.CharField(db_index=True, help_text="Internal page key, for example: home, about, services_list, project_detail.", max_length=80)),
                ("page_label", models.CharField(blank=True, max_length=160)),
                ("section_key", models.SlugField(help_text="Internal section key used by templates.", max_length=120)),
                ("section_label", models.CharField(max_length=180)),
                ("description", models.TextField(blank=True)),
                ("sort_order", models.PositiveIntegerField(default=100, help_text="Lower number shows earlier. Example: 10 appears before 20.")),
                ("is_active", models.BooleanField(default=True, help_text="Disable to hide this section everywhere this page template uses it.")),
            ],
            options={
                "verbose_name": "Page section order",
                "verbose_name_plural": "Page section order",
                "ordering": ["page_key", "sort_order", "id"],
                "unique_together": {("page_key", "section_key")},
            },
        ),
        migrations.RunPython(seed_section_order, migrations.RunPython.noop),
    ]
