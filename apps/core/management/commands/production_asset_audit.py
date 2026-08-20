
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
from django.db.models import FileField, ImageField


IMPORTANT_STATIC_ASSETS = [
    "img/brand/sescco-mark.webp",
    "img/brand/sescco-logo.svg",
    "img/brand/sescco_logo.svg",
    "img/fallbacks/industrial-fallback.svg",
    "css/style.css",
    "css/rtl.css",
    "js/main.js",
]


class Command(BaseCommand):
    help = "Audit production media/static assets referenced by CMS records and templates."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="Fail when missing required assets are found.")
        parser.add_argument("--output", help="Optional Markdown report path, for example reports/production-asset-audit.md")
        parser.add_argument("--skip-media", action="store_true", help="Only check required static assets.")

    def handle(self, *args, **options):
        missing_static = self._check_static_assets()
        missing_media = [] if options["skip_media"] else self._check_media_fields()
        warnings = []

        if not missing_static and not missing_media:
            self.stdout.write(self.style.SUCCESS("Production asset audit passed: no missing static/media references found."))
        else:
            if missing_static:
                self.stdout.write(self.style.WARNING(f"Missing static assets: {len(missing_static)}"))
            if missing_media:
                self.stdout.write(self.style.WARNING(f"Missing CMS media files: {len(missing_media)}"))

        report = self._build_report(missing_static, missing_media, warnings)
        if options.get("output"):
            output_path = Path(options["output"])
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Asset audit report written to {output_path}"))

        if options["strict"] and (missing_static or missing_media):
            raise CommandError("Production asset audit failed. Fix missing static/media references before deployment.")

    def _check_static_assets(self):
        missing = []
        for asset in IMPORTANT_STATIC_ASSETS:
            if not finders.find(asset):
                missing.append(asset)
        return missing

    def _check_media_fields(self):
        missing = []
        for model in apps.get_models():
            file_fields = [field for field in model._meta.fields if isinstance(field, (FileField, ImageField))]
            if not file_fields:
                continue
            queryset = model._default_manager.all()
            for obj in queryset.iterator():
                for field in file_fields:
                    value = getattr(obj, field.name, None)
                    if not value:
                        continue
                    try:
                        if not value.storage.exists(value.name):
                            missing.append({
                                "model": model._meta.label,
                                "object": str(obj),
                                "field": field.name,
                                "file": value.name,
                            })
                    except Exception as exc:
                        # Remote/private storages may deny path inspection. Treat this as a warning-level
                        # missing entry so production review notices the issue instead of silently passing.
                        missing.append({
                            "model": model._meta.label,
                            "object": str(obj),
                            "field": field.name,
                            "file": value.name,
                            "error": str(exc),
                        })
        return missing

    def _build_report(self, missing_static, missing_media, warnings):
        lines = [
            "# SESCCO Production Asset Audit", "",
            "This report verifies that required static files and CMS media references are available before deployment.", "",
            "## Summary", "",
            f"- Missing required static assets: {len(missing_static)}",
            f"- Missing CMS media references: {len(missing_media)}",
            f"- Warnings: {len(warnings)}", "",
        ]
        lines.extend(["## Required Static Assets", ""])
        if missing_static:
            for asset in missing_static:
                lines.append(f"- Missing: `{asset}`")
        else:
            lines.append("- Passed: all required static assets are discoverable by Django staticfiles.")
        lines.extend(["", "## CMS Media References", ""])
        if missing_media:
            for item in missing_media:
                extra = f" Error: {item.get('error')}" if item.get("error") else ""
                lines.append(f"- `{item['model']}.{item['field']}` on `{item['object']}` references `{item['file']}`.{extra}")
        else:
            lines.append("- Passed: all populated FileField/ImageField references exist in the configured storage.")
        if warnings:
            lines.extend(["", "## Warnings", ""])
            lines.extend([f"- {warning}" for warning in warnings])
        lines.append("")
        return "\n".join(lines)
