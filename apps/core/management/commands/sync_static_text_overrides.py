import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.models import LocalizedContent
from apps.core.templatetags.localization import STATIC_TRANSLATIONS, static_text_id


STATIC_TEXT_RE = re.compile(r"\{\%\s*static_text\s+(?:\"([^\"]+)\"|'([^']+)')\s*\%\}")


class Command(BaseCommand):
    help = "Create/update admin-editable LocalizedContent rows for every {% static_text %} label used in templates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing records with current defaults. By default existing admin edits are preserved.",
        )

    def handle(self, *args, **options):
        template_dir = Path(settings.BASE_DIR) / "templates"
        source_texts = set()
        if template_dir.exists():
            for template_path in template_dir.rglob("*.html"):
                content = template_path.read_text(encoding="utf-8", errors="ignore")
                for match in STATIC_TEXT_RE.finditer(content):
                    source_texts.add(match.group(1) or match.group(2) or "")

        for translations in STATIC_TRANSLATIONS.values():
            source_texts.update(translations.keys())

        source_texts = {item.strip() for item in source_texts if item and item.strip()}
        languages = ["en", "ar", "zh-hans"]
        created = 0
        updated = 0
        skipped = 0

        for source_text in sorted(source_texts, key=str.lower):
            object_id = static_text_id(source_text)
            for language_code in languages:
                default_text = source_text if language_code == "en" else STATIC_TRANSLATIONS.get(language_code, {}).get(source_text, "")
                if not default_text:
                    continue
                obj, was_created = LocalizedContent.objects.get_or_create(
                    content_type="statictext",
                    object_id=object_id,
                    language_code=language_code,
                    field_name="text",
                    defaults={"text": default_text},
                )
                if was_created:
                    created += 1
                elif options["update_existing"]:
                    obj.text = default_text
                    obj.save(update_fields=["text", "updated_at"])
                    updated += 1
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Static UI text sync complete. Created: {created}. Updated: {updated}. Preserved existing: {skipped}."
        ))
