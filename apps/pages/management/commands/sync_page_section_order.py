from django.core.management.base import BaseCommand

from apps.pages.models import PageSectionOrder
from apps.pages.section_registry import iter_default_sections


class Command(BaseCommand):
    help = "Create/update admin-editable page section ordering records for every major page template."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-order",
            action="store_true",
            help="Reset priorities to the simple default order: 1, 2, 3, 4...",
        )
        parser.add_argument(
            "--prune-obsolete",
            action="store_true",
            help="Delete section-order rows for page groups that are no longer used, such as the removed Downloads page.",
        )

    def handle(self, *args, **options):
        created = 0
        updated = 0
        order_reset = 0
        deleted = 0
        reset_order = options.get("reset_order", False)
        defaults = list(iter_default_sections())
        valid_pairs = {(section["page_key"], section["section_key"]) for section in defaults}

        if options.get("prune_obsolete", False):
            obsolete_ids = []
            for row in PageSectionOrder.objects.all().only("id", "page_key", "section_key"):
                if (row.page_key, row.section_key) not in valid_pairs:
                    obsolete_ids.append(row.id)
            if obsolete_ids:
                deleted, _ = PageSectionOrder.objects.filter(id__in=obsolete_ids).delete()

        for section in defaults:
            obj, was_created = PageSectionOrder.objects.get_or_create(
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
            if was_created:
                created += 1
                continue
            changed = False
            for field in ["page_label", "section_label", "description"]:
                if getattr(obj, field) != section[field]:
                    setattr(obj, field, section[field])
                    changed = True
            if reset_order and obj.sort_order != section["sort_order"]:
                obj.sort_order = section["sort_order"]
                changed = True
                order_reset += 1
            if changed:
                update_fields = ["page_label", "section_label", "description", "updated_at"]
                if reset_order:
                    update_fields.append("sort_order")
                obj.save(update_fields=update_fields)
                updated += 1
        message = f"Page section order synced. Created: {created}. Updated labels: {updated}."
        if reset_order:
            message += f" Reset priority values: {order_reset}."
        if options.get("prune_obsolete", False):
            message += f" Removed obsolete rows: {deleted}."
        self.stdout.write(self.style.SUCCESS(message))
