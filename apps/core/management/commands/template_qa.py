from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Check templates for common syntax mistakes introduced during upgrades."

    def handle(self, *args, **options):
        template_dir = Path(settings.BASE_DIR) / "templates"
        issues = []

        for path in template_dir.rglob("*.html"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "{% static \\'" in text or '{% static \\"' in text:
                issues.append(f"{path.relative_to(settings.BASE_DIR)} has escaped quotes inside static tag.")
            if "{% extends" in text:
                stripped = [line.strip() for line in text.splitlines() if line.strip()]
                if stripped and stripped[0].startswith("{% load") and len(stripped) > 1 and stripped[1].startswith("{% extends"):
                    issues.append(f"{path.relative_to(settings.BASE_DIR)} has load before extends.")

        if issues:
            self.stdout.write(self.style.WARNING("Template QA issues found:"))
            for issue in issues:
                self.stdout.write(f"- {issue}")
        else:
            self.stdout.write(self.style.SUCCESS("Template QA passed."))
