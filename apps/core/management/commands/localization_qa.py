import re
from django.core.management.base import BaseCommand
from apps.core.models import LocalizedContent
from apps.core.translation_registry import TRANSLATION_TARGETS


LATIN_RE = re.compile(r"[A-Za-z]{4,}")


class Command(BaseCommand):
    help = "Run localization QA checks for Arabic and Chinese override coverage and old demo artifacts."

    def handle(self, *args, **options):
        languages = ["ar", "zh-hans"]
        self.stdout.write(self.style.HTTP_INFO("Localization QA Report"))

        bad_prefixes = ("ترجمة:", "Translation:", "翻译:")
        for lang in languages:
            self.stdout.write(self.style.HTTP_INFO(f"\nLanguage: {lang}"))
            total = 0
            empty = 0
            bad_demo = 0
            latin_suspected = 0

            for target in TRANSLATION_TARGETS:
                qs = LocalizedContent.objects.filter(content_type=target.content_type, language_code=lang)
                count = qs.count()
                empty_count = qs.filter(text="").count()
                bad_count = 0
                latin_count = 0

                for item in qs[:2000]:
                    text = str(item.text or "").strip()
                    if text.startswith(bad_prefixes):
                        bad_count += 1
                    # Arabic should not have long English phrases, but brand names/emails may appear.
                    if lang == "ar" and LATIN_RE.search(text) and "@" not in text and "http" not in text:
                        latin_count += 1

                total += count
                empty += empty_count
                bad_demo += bad_count
                latin_suspected += latin_count

                status = "OK" if count else "MISSING"
                self.stdout.write(f"{target.model_label:34} {count:4} {status}")

            self.stdout.write(self.style.SUCCESS(
                f"Total records: {total}; Empty: {empty}; Bad demo prefixes: {bad_demo}; Latin suspected in Arabic: {latin_suspected}"
            ))

        self.stdout.write("\nManual QA:")
        self.stdout.write("- Compare /contact/ with /ar/contact/ and /zh-hans/contact/")
        self.stdout.write("- Compare /clients-certifications/ with /ar/clients-certifications/")
        self.stdout.write("- Click every nav item while in Arabic; URL should stay under /ar/.")
        self.stdout.write("- Proper names, phone numbers, emails, vendor codes may stay unchanged.")
        self.stdout.write("\nTemplate static text reminders:")
        self.stdout.write("- If English remains, replace hardcoded template text with `{% static_text \"Text\" %}`.")
        self.stdout.write("- If CMS content remains English, add/edit LocalizedContent records from /admin/core/localizedcontent/.")
