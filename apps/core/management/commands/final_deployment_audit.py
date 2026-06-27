from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import get_template
from django.urls import NoReverseMatch, reverse


class Command(BaseCommand):
    help = "Run the final SESCCO deployment gate before production launch."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="Exit with error if launch-blocking issues are found.")
        parser.add_argument("--output", default="", help="Optional Markdown report path.")
        parser.add_argument("--skip-child-audits", action="store_true", help="Only run final deployment checks, not the data/language/asset/admin audits.")

    def _add(self, rows, level, message, fix=""):
        rows.append({"level": level, "message": message, "fix": fix})

    def _run_child_audit(self, command_name, rows):
        buffer = StringIO()
        try:
            call_command(command_name, strict=True, stdout=buffer)
            self._add(rows, "PASS", f"{command_name} strict audit passed.")
        except Exception as exc:
            self._add(rows, "ERROR", f"{command_name} strict audit failed: {exc}", f"Run `python manage.py {command_name} --strict --output reports/{command_name}.md` and fix the report.")

    def handle(self, *args, **options):
        rows = []

        # Production settings checks.
        if settings.DEBUG:
            self._add(rows, "ERROR", "DEBUG is enabled.", "Use config.settings.production and set DEBUG=False.")
        else:
            self._add(rows, "PASS", "DEBUG is disabled.")

        secret_key = getattr(settings, "SECRET_KEY", "")
        if not secret_key or secret_key == "dev-insecure-change-me" or len(secret_key) < 40:
            self._add(rows, "ERROR", "SECRET_KEY is missing, default, or too short.", "Set a long random SECRET_KEY in production environment variables.")
        else:
            self._add(rows, "PASS", "SECRET_KEY is production-shaped.")

        allowed_hosts = list(getattr(settings, "ALLOWED_HOSTS", []))
        if not allowed_hosts or "*" in allowed_hosts or allowed_hosts == ["127.0.0.1", "localhost"]:
            self._add(rows, "ERROR", "ALLOWED_HOSTS is not production-specific.", "Set ALLOWED_HOSTS=sescco.com,www.sescco.com,<server-ip-or-host>.")
        else:
            self._add(rows, "PASS", f"ALLOWED_HOSTS configured: {', '.join(allowed_hosts)}")

        required_security = [
            ("SECURE_SSL_REDIRECT", True),
            ("SESSION_COOKIE_SECURE", True),
            ("CSRF_COOKIE_SECURE", True),
            ("SECURE_CONTENT_TYPE_NOSNIFF", True),
            ("X_FRAME_OPTIONS", "DENY"),
        ]
        for setting_name, expected in required_security:
            value = getattr(settings, setting_name, None)
            if value != expected:
                self._add(rows, "ERROR", f"{setting_name} is {value!r}; expected {expected!r}.", "Check config/settings/production.py and production environment overrides.")
            else:
                self._add(rows, "PASS", f"{setting_name} is correctly set.")

        if getattr(settings, "SECURE_HSTS_SECONDS", 0) < 31536000:
            self._add(rows, "WARN", "HSTS is below one year.", "Use one year after confirming HTTPS is stable.")
        else:
            self._add(rows, "PASS", "HSTS is configured for production.")

        if getattr(settings, "EMAIL_BACKEND", "").endswith("console.EmailBackend"):
            self._add(rows, "WARN", "EMAIL_BACKEND is console backend.", "Use SMTP/API email backend before accepting production forms/applications.")
        else:
            self._add(rows, "PASS", "EMAIL_BACKEND is not console backend.")

        # Template and URL checks.
        for template_name in ["base.html", "errors/404.html", "errors/500.html", "includes/header.html", "includes/footer.html"]:
            try:
                get_template(template_name)
                self._add(rows, "PASS", f"Template available: {template_name}")
            except Exception as exc:
                self._add(rows, "ERROR", f"Template missing/broken: {template_name}: {exc}")

        named_urls = [
            "home", "about", "service_list", "project_list", "clients_certifications",
            "downloads", "career_list", "contact", "localized_sitemap", "robots_txt", "healthz",
        ]
        for name in named_urls:
            try:
                reverse(name)
                self._add(rows, "PASS", f"URL resolves: {name}")
            except NoReverseMatch as exc:
                self._add(rows, "ERROR", f"URL does not resolve: {name}: {exc}")

        static_root = Path(getattr(settings, "STATIC_ROOT", ""))
        media_root = Path(getattr(settings, "MEDIA_ROOT", ""))
        if not getattr(settings, "STATICFILES_STORAGE", ""):
            self._add(rows, "WARN", "STATICFILES_STORAGE is empty.", "Use ManifestStaticFilesStorage or WhiteNoise compressed manifest storage.")
        else:
            self._add(rows, "PASS", "Static files storage is configured.")
        if not media_root:
            self._add(rows, "ERROR", "MEDIA_ROOT is empty.", "Set MEDIA_ROOT or external media storage.")
        else:
            self._add(rows, "PASS", f"MEDIA_ROOT configured: {media_root}")
        if not static_root:
            self._add(rows, "ERROR", "STATIC_ROOT is empty.", "Set STATIC_ROOT for collectstatic.")
        else:
            self._add(rows, "PASS", f"STATIC_ROOT configured: {static_root}")

        if not options.get("skip_child_audits"):
            for command_name in ["production_data_audit", "multilingual_content_audit", "production_asset_audit", "production_admin_audit"]:
                self._run_child_audit(command_name, rows)

        errors = [r for r in rows if r["level"] == "ERROR"]
        warnings = [r for r in rows if r["level"] == "WARN"]

        self.stdout.write(self.style.HTTP_INFO("SESCCO Final Deployment Audit"))
        for row in rows:
            style = self.style.SUCCESS if row["level"] == "PASS" else self.style.WARNING if row["level"] == "WARN" else self.style.ERROR
            self.stdout.write(style(f"[{row['level']}] {row['message']}"))
            if row.get("fix"):
                self.stdout.write(f"      Fix: {row['fix']}")

        self.stdout.write("")
        self.stdout.write(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s), {len(rows) - len(errors) - len(warnings)} pass(es).")

        if options.get("output"):
            report_path = Path(options["output"])
            report_path.parent.mkdir(parents=True, exist_ok=True)
            lines = ["# SESCCO Final Deployment Audit", "", f"Errors: {len(errors)}", f"Warnings: {len(warnings)}", "", "| Level | Check | Fix |", "|---|---|---|"]
            for row in rows:
                lines.append(f"| {row['level']} | {row['message'].replace('|', '/')} | {row.get('fix', '').replace('|', '/')} |")
            report_path.write_text("\n".join(lines), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Report written to {report_path}"))

        if errors and options.get("strict"):
            raise CommandError(f"Final deployment audit failed with {len(errors)} error(s).")
        if not errors:
            self.stdout.write(self.style.SUCCESS("Final deployment audit passed. Site is ready for live production QA."))
