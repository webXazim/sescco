from django.db import migrations
from django.db.models import Q


TELECOM_PROJECT_TITLES = [
    "Ethernet Cable Installation and Testing Works",
    "Telecommunication Cabinet and Network Support Works",
    "SEPCO Telecommunication Field Support Works",
    "OPGW Fiber Splicing and Testing Works",
]


def set_localized_name(LocalizedContent, category, language_code, text):
    LocalizedContent.objects.update_or_create(
        content_type="projectcategory",
        object_id=category.id,
        language_code=language_code,
        field_name="name",
        defaults={"text": text},
    )


def forwards(apps, schema_editor):
    ProjectCategory = apps.get_model("projects", "ProjectCategory")
    Project = apps.get_model("projects", "Project")
    ProjectListPageSettings = apps.get_model("projects", "ProjectListPageSettings")
    LocalizedContent = apps.get_model("core", "LocalizedContent")

    category, _ = ProjectCategory.objects.update_or_create(
        slug="telecommunication-projects",
        defaults={
            "name": "Telecommunication Projects",
            "icon_text": "",
            "sort_order": 2,
            "is_active": True,
        },
    )

    category_order = {
        "electrical-projects": 1,
        "telecommunication-projects": 2,
        "civil-projects": 3,
        "architectural-fitout-projects": 4,
        "mechanical-projects": 5,
    }
    for slug, sort_order in category_order.items():
        ProjectCategory.objects.filter(slug=slug).update(sort_order=sort_order)

    telecom_projects = Project.objects.filter(
        Q(title__in=TELECOM_PROJECT_TITLES)
        | Q(services__slug="telecommunication-services")
    ).distinct()
    telecom_projects.update(category=category)

    ProjectListPageSettings.objects.filter(
        hero_subtitle="SESCCO’s portfolio includes electrical, civil, architectural fit-out, pipeline, mechanical and support projects."
    ).update(
        hero_subtitle="SESCCO’s portfolio includes electrical, telecommunication, civil, architectural fit-out, pipeline, mechanical and support projects."
    )

    set_localized_name(LocalizedContent, category, "ar", "مشاريع الاتصالات")
    set_localized_name(LocalizedContent, category, "zh-hans", "通信项目")


def backwards(apps, schema_editor):
    ProjectCategory = apps.get_model("projects", "ProjectCategory")
    Project = apps.get_model("projects", "Project")
    LocalizedContent = apps.get_model("core", "LocalizedContent")

    telecom_category = ProjectCategory.objects.filter(slug="telecommunication-projects").first()
    electrical_category = ProjectCategory.objects.filter(slug="electrical-projects").first()
    if telecom_category and electrical_category:
        Project.objects.filter(category=telecom_category).update(category=electrical_category)
        LocalizedContent.objects.filter(
            content_type="projectcategory",
            object_id=telecom_category.id,
        ).delete()
        telecom_category.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0005_project_slug_length"),
        ("core", "0010_production_client_request_cleanup"),
    ]

    operations = [migrations.RunPython(forwards, backwards)]
