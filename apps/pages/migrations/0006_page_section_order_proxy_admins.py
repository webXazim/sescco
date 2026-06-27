from django.db import migrations, models


def normalize_section_priorities(apps, schema_editor):
    PageSectionOrder = apps.get_model("pages", "PageSectionOrder")
    from apps.pages.section_registry import iter_default_sections

    for section in iter_default_sections():
        obj, _ = PageSectionOrder.objects.get_or_create(
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
        old_tens_value = section["sort_order"] * 10
        update_fields = []
        for field in ["page_label", "section_label", "description"]:
            if getattr(obj, field) != section[field]:
                setattr(obj, field, section[field])
                update_fields.append(field)
        if obj.sort_order == old_tens_value:
            obj.sort_order = section["sort_order"]
            update_fields.append("sort_order")
        if update_fields:
            obj.save(update_fields=update_fields)


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0005_pagesectionorder"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pagesectionorder",
            name="sort_order",
            field=models.PositiveIntegerField(default=1, help_text="Priority number. 1 shows first, 2 shows second, 3 shows third. Keep it simple: use 1, 2, 3, 4, 5."),
        ),
        migrations.CreateModel(
            name="HomeSectionOrder",
            fields=[],
            options={"verbose_name": "Home section order", "verbose_name_plural": "Home section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="AboutSectionOrder",
            fields=[],
            options={"verbose_name": "About section order", "verbose_name_plural": "About section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="ServicesListSectionOrder",
            fields=[],
            options={"verbose_name": "Services list section order", "verbose_name_plural": "Services list section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="ServiceDetailSectionOrder",
            fields=[],
            options={"verbose_name": "Service detail section order", "verbose_name_plural": "Service detail section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="ProjectsListSectionOrder",
            fields=[],
            options={"verbose_name": "Projects list section order", "verbose_name_plural": "Projects list section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="ProjectDetailSectionOrder",
            fields=[],
            options={"verbose_name": "Project detail section order", "verbose_name_plural": "Project detail section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="ClientsCertificationsSectionOrder",
            fields=[],
            options={"verbose_name": "Certifications & clients section order", "verbose_name_plural": "Certifications & clients section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="CareersSectionOrder",
            fields=[],
            options={"verbose_name": "Careers section order", "verbose_name_plural": "Careers section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="ContactSectionOrder",
            fields=[],
            options={"verbose_name": "Contact section order", "verbose_name_plural": "Contact section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="DownloadsSectionOrder",
            fields=[],
            options={"verbose_name": "Downloads section order", "verbose_name_plural": "Downloads section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.CreateModel(
            name="GenericSectionOrder",
            fields=[],
            options={"verbose_name": "Generic page section order", "verbose_name_plural": "Generic page section order", "proxy": True, "indexes": [], "constraints": []},
            bases=("pages.pagesectionorder",),
        ),
        migrations.RunPython(normalize_section_priorities, migrations.RunPython.noop),
    ]
