from django.db import migrations


def apply_home_sphere_visual_cards_only(apps, schema_editor):
    HomeHeroSphereCard = apps.get_model("pages", "HomeHeroSphereCard")
    # Remove duplicate overlay copy from existing seeded/admin image cards.
    HomeHeroSphereCard.objects.filter(card_type="image").update(subtitle="", big_text="")
    # Disable old text/data cards. The home hero stat strip already carries metrics,
    # and the visual sphere should only show image artwork.
    HomeHeroSphereCard.objects.filter(card_type="data").update(is_featured=False, is_active=False)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0011_certifications_clients_section_order"),
    ]

    operations = [
        migrations.RunPython(apply_home_sphere_visual_cards_only, reverse_noop),
    ]
