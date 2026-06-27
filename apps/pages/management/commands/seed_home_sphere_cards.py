from django.core.management.base import BaseCommand
from apps.pages.models import HomeHeroSphereCard


DEFAULT_CARDS = [
    {"card_type": "image", "title": "Industrial Construction", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_01_industrial_construction.webp"},
    {"card_type": "image", "title": "Electrical Works", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_02_electrical_works.webp"},
    {"card_type": "image", "title": "Project Control", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_03_project_control.webp"},
    {"card_type": "image", "title": "Safety Management", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_04_safety_management.webp"},
    {"card_type": "image", "title": "QA Inspection", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_05_qa_inspection.webp"},
    {"card_type": "image", "title": "Site Engineering", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_06_site_engineering.webp"},
    {"card_type": "image", "title": "Substation Works", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_07_substation_works.webp"},
    {"card_type": "image", "title": "Pipeline Fabrication", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_08_pipeline_fabrication.webp"},
    {"card_type": "image", "title": "MEP Coordination", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_09_mep_coordination.webp"},
    {"card_type": "image", "title": "Civil Site Team", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch1_10_civil_site_team.webp"},
    {"card_type": "image", "title": "Structural Steel Erection", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_01_structural_steel_erection.webp"},
    {"card_type": "image", "title": "HVAC Systems", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_02_hvac_systems.webp"},
    {"card_type": "image", "title": "Fire Protection", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_03_fire_protection.webp"},
    {"card_type": "image", "title": "Instrumentation & Control", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_04_instrumentation_control.webp"},
    {"card_type": "image", "title": "Telecom Infrastructure", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_05_telecom_infrastructure.webp"},
    {"card_type": "image", "title": "Water Treatment", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_06_water_treatment.webp"},
    {"card_type": "image", "title": "Solar Energy", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_07_solar_energy.webp"},
    {"card_type": "image", "title": "Survey & Earthworks", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_08_survey_earthworks.webp"},
    {"card_type": "image", "title": "Warehouse Logistics", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_09_warehouse_logistics.webp"},
    {"card_type": "image", "title": "Industrial Automation", "subtitle": "", "static_image_path": "img/hero_sphere/optimized/batch2_10_industrial_automation.webp"},
]


class Command(BaseCommand):
    help = "Seed default home hero sphere cards for admin editing."

    def handle(self, *args, **options):
        created = 0
        for order, data in enumerate(DEFAULT_CARDS, start=1):
            obj, was_created = HomeHeroSphereCard.objects.get_or_create(
                title=data["title"],
                defaults={
                    **data,
                    "sort_order": order,
                    "is_active": True,
                    "is_featured": True,
                },
            )
            if was_created:
                created += 1
            else:
                # Keep the command useful after this image upgrade:
                # update only the default technical fields while preserving active/featured choices.
                for field, value in data.items():
                    setattr(obj, field, value)
                obj.sort_order = order
                obj.save()
        # Text/data cards were used in early sphere versions. The current visual sphere
        # uses only image cards because each card artwork already contains its own text.
        HomeHeroSphereCard.objects.filter(card_type="data").update(is_featured=False, is_active=False)
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new image card(s), removed overlay subtitles, and disabled old text/data sphere cards."))
