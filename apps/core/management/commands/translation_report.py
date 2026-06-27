from django.core.management.base import BaseCommand
from apps.core.models import LocalizedContent
from apps.core.translation_registry import TRANSLATION_TARGETS


class Command(BaseCommand):
    help = "Show a simple translation count report by content type and language."

    def add_arguments(self, parser):
        parser.add_argument("--language", default="ar", help="Language code, e.g. ar or zh-hans")

    def handle(self, *args, **options):
        language = options["language"]
        self.stdout.write(self.style.HTTP_INFO(f"Translation report for: {language}"))
        for target in TRANSLATION_TARGETS:
            count = LocalizedContent.objects.filter(content_type=target.content_type, language_code=language).count()
            self.stdout.write(f"{target.model_label:32} {target.content_type:28} {count}")
