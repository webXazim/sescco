from django.core.management.base import BaseCommand
from apps.core.models import LocalizedContent
from apps.core.translation_registry import TRANSLATION_TARGETS


class Command(BaseCommand):
    help = "Create empty translation draft records for objects that already have English/default content. This is a helper skeleton command."

    def add_arguments(self, parser):
        parser.add_argument("--language", default="ar", help="Language code, e.g. ar or zh-hans")

    def handle(self, *args, **options):
        language = options["language"]
        self.stdout.write(self.style.WARNING(
            "This project uses a safe override translation system. "
            "Use seed_localization for broad demo drafts, or add translations in admin. "
            "Full automatic object discovery will be added in the next localization admin upgrade if needed."
        ))
        self.stdout.write(self.style.SUCCESS(f"Language selected: {language}"))
