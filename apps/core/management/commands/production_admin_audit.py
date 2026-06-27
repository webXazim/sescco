from collections import defaultdict
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count


SINGLETON_MODELS = [
    ("core", "CompanyProfile"),
    ("core", "SiteSettings"),
    ("core", "ThemeSettings"),
    ("core", "CTASettings"),
    ("services", "ServiceListPageSettings"),
    ("services", "ServiceDetailPageSettings"),
    ("projects", "ProjectListPageSettings"),
    ("projects", "ProjectDetailPageSettings"),
    ("documents", "DocumentPageCTA"),
    ("inquiries", "ContactPageSettings"),
    ("clients", "TrustPageSettings"),
    ("careers", "CareerPageSettings"),
    ("seo", "RobotsSettings"),
    ("pages", "HomeHero"),
    ("pages", "HomeAboutBlock"),
    ("pages", "HomeSectionSettings"),
]

SLUG_MODELS = [
    ("pages", "Page", "slug"),
    ("services", "Service", "slug"),
    ("services", "ServiceCategory", "slug"),
    ("projects", "Project", "slug"),
    ("projects", "ProjectCategory", "slug"),
    ("documents", "DocumentCategory", "slug"),
    ("clients", "ClientCategory", "slug"),
    ("clients", "CertificateCategory", "slug"),
    ("careers", "CareerDepartment", "slug"),
    ("careers", "JobOpening", "slug"),
]

ACTIVE_TEXT_MODELS = [
    ("core", "NavigationMenu", ["title", "url"]),
    ("core", "FooterColumn", ["title"]),
    ("core", "FooterLink", ["title", "url"]),
    ("core", "SocialLink", ["title", "url"]),
    ("core", "TrustMetric", ["title", "value"]),
    ("core", "CTASection", ["title"]),
    ("core", "OfficeLocation", ["name", "address"]),
    ("pages", "Page", ["title", "slug"]),
    ("pages", "PageSection", ["title"]),
    ("pages", "FAQ", ["question", "answer"]),
    ("services", "Service", ["title", "slug", "short_description", "body"]),
    ("services", "ServiceFAQ", ["question", "answer"]),
    ("services", "ServiceFeature", ["title", "description"]),
    ("services", "ServiceDeliverable", ["title"]),
    ("projects", "Project", ["title", "slug", "short_description", "summary"]),
    ("projects", "ProjectScopeItem", ["title", "description"]),
    ("documents", "DownloadDocument", ["title", "description"]),
    ("clients", "Client", ["name"]),
    ("clients", "Certificate", ["title"]),
    ("careers", "JobOpening", ["title", "slug", "summary"]),
]

UNIQUE_SORT_SCOPES = [
    ("core", "NavigationMenu", [], "Main navigation"),
    ("core", "FooterColumn", [], "Footer columns"),
    ("pages", "PageSection", ["page_id"], "Page sections per page"),
    ("services", "ServiceFAQ", ["service_id"], "Service FAQs per service"),
    ("services", "ServiceFeature", ["service_id"], "Service features per service"),
    ("services", "ServiceDeliverable", ["service_id"], "Service deliverables per service"),
    ("projects", "ProjectScopeItem", ["project_id"], "Project scope items per project"),
    ("projects", "ProjectMetric", ["project_id"], "Project metrics per project"),
    ("documents", "DownloadDocument", ["category_id"], "Documents per category"),
]


class AuditResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def ok(self, msg):
        self.passed.append(msg)


def get_model(app_label, model_name):
    try:
        return apps.get_model(app_label, model_name)
    except LookupError:
        return None


def safe_str(value):
    return str(value or "").strip()


class Command(BaseCommand):
    help = "Audit admin-facing CMS safety: duplicate singletons, duplicate slugs, empty active records, and risky ordering."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="Fail when production-blocking admin safety issues are found.")
        parser.add_argument("--output", help="Optional Markdown report path, for example reports/production-admin-audit.md")

    def handle(self, *args, **options):
        result = AuditResult()
        self.check_singletons(result)
        self.check_duplicate_slugs(result)
        self.check_active_required_content(result)
        self.check_sort_order_collisions(result)
        self.write_console(result)
        if options.get("output"):
            self.write_report(result, options["output"])
        if options.get("strict") and result.errors:
            raise CommandError(f"Production admin audit failed with {len(result.errors)} blocking issue(s).")

    def check_singletons(self, result):
        for app_label, model_name in SINGLETON_MODELS:
            model = get_model(app_label, model_name)
            if model is None:
                result.warn(f"Singleton model not found: {app_label}.{model_name}")
                continue
            count = model.objects.count()
            if count > 1:
                result.error(f"{app_label}.{model_name} has {count} rows but should have only one. Keep the newest valid row and remove duplicates.")
            elif count == 0:
                result.warn(f"{app_label}.{model_name} has no row. Run seed_sescco_production before launch.")
            else:
                result.ok(f"{app_label}.{model_name} singleton is safe.")

    def check_duplicate_slugs(self, result):
        for app_label, model_name, field in SLUG_MODELS:
            model = get_model(app_label, model_name)
            if model is None or not hasattr(model, field):
                continue
            rows = (
                model.objects.exclude(**{f"{field}__isnull": True})
                .exclude(**{field: ""})
                .values(field)
                .annotate(total=Count("id"))
                .filter(total__gt=1)
            )
            duplicates = list(rows)
            if duplicates:
                for row in duplicates:
                    result.error(f"Duplicate {field} in {app_label}.{model_name}: '{row[field]}' appears {row['total']} times.")
            else:
                result.ok(f"{app_label}.{model_name} {field} values are unique.")

    def check_active_required_content(self, result):
        for app_label, model_name, fields in ACTIVE_TEXT_MODELS:
            model = get_model(app_label, model_name)
            if model is None:
                continue
            qs = model.objects.all()
            if hasattr(model, "is_active"):
                qs = qs.filter(is_active=True)
            elif hasattr(model, "is_published"):
                qs = qs.filter(is_published=True)
            checked = 0
            for obj in qs[:500]:
                checked += 1
                for field in fields:
                    if not hasattr(obj, field):
                        continue
                    value = safe_str(getattr(obj, field, ""))
                    if not value:
                        label = safe_str(getattr(obj, "title", getattr(obj, "name", getattr(obj, "slug", obj.pk))))
                        result.warn(f"Active {app_label}.{model_name} #{obj.pk} ({label}) has empty admin-visible field: {field}.")
            if checked:
                result.ok(f"Checked {checked} active {app_label}.{model_name} record(s) for empty content.")

    def check_sort_order_collisions(self, result):
        for app_label, model_name, scope_fields, label in UNIQUE_SORT_SCOPES:
            model = get_model(app_label, model_name)
            if model is None or not hasattr(model, "sort_order"):
                continue
            values = list(scope_fields) + ["sort_order"]
            qs = model.objects.all()
            if hasattr(model, "is_active"):
                qs = qs.filter(is_active=True)
            rows = qs.values(*values).annotate(total=Count("id")).filter(total__gt=1).order_by("sort_order")
            collisions = list(rows)
            if collisions:
                for row in collisions:
                    scope = ", ".join(f"{f}={row.get(f)}" for f in scope_fields) or "global"
                    result.warn(f"{label}: duplicate active sort_order={row['sort_order']} in {scope} ({row['total']} rows).")
            else:
                result.ok(f"{label} ordering has no duplicate active sort positions.")

    def write_console(self, result):
        self.stdout.write(self.style.MIGRATE_HEADING("Production admin safety audit"))
        self.stdout.write(f"Passed: {len(result.passed)}")
        self.stdout.write(f"Warnings: {len(result.warnings)}")
        self.stdout.write(f"Errors: {len(result.errors)}")
        for msg in result.errors:
            self.stdout.write(self.style.ERROR(f"ERROR: {msg}"))
        for msg in result.warnings[:50]:
            self.stdout.write(self.style.WARNING(f"WARN: {msg}"))
        if len(result.warnings) > 50:
            self.stdout.write(self.style.WARNING(f"... {len(result.warnings) - 50} more warning(s). Use --output for full report."))
        if not result.errors:
            self.stdout.write(self.style.SUCCESS("No production-blocking admin safety issues found."))

    def write_report(self, result, output_path):
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# SESCCO Production Admin Safety Audit",
            "",
            f"- Passed checks: {len(result.passed)}",
            f"- Warnings: {len(result.warnings)}",
            f"- Blocking errors: {len(result.errors)}",
            "",
            "## Blocking Errors",
        ]
        lines.extend([f"- {msg}" for msg in result.errors] or ["- None"])
        lines.append("")
        lines.append("## Warnings")
        lines.extend([f"- {msg}" for msg in result.warnings] or ["- None"])
        lines.append("")
        lines.append("## Passed Checks")
        lines.extend([f"- {msg}" for msg in result.passed])
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Admin safety report written to {path}"))
