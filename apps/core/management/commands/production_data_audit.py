from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.html import strip_tags

from apps.clients.models import Certificate, Client, Partner
from apps.core.models import CompanyProfile, LocalizedContent, NavigationMenu, SiteSettings, TrustMetric
from apps.documents.models import DownloadDocument
from apps.pages.models import FAQ, HomeAboutBlock, HomeHero, HomeHighlight, Page, PageSection, WhyChooseItem
from apps.projects.models import Project, ProjectListStat
from apps.services.models import Service, ServiceCategory, ServiceListFAQ


LANGUAGES = ("ar", "zh-hans")


class AuditIssue:
    def __init__(self, severity: str, area: str, message: str):
        self.severity = severity
        self.area = area
        self.message = message

    @property
    def is_error(self) -> bool:
        return self.severity == "ERROR"

    def as_line(self) -> str:
        return f"[{self.severity}] {self.area}: {self.message}"


class Command(BaseCommand):
    help = "Audit SESCCO seeded CMS data for production completeness, translations, SEO and empty public sections."

    def add_arguments(self, parser):
        parser.add_argument(
            "--strict",
            action="store_true",
            help="Exit with an error when production-blocking issues are found.",
        )
        parser.add_argument(
            "--output",
            default="",
            help="Optional Markdown report path, for example reports/production-data-audit.md.",
        )

    def handle(self, *args, **options):
        issues: list[AuditIssue] = []
        counters: dict[str, int] = {}

        self._audit_core(issues, counters)
        self._audit_page_content(issues, counters)
        self._audit_services(issues, counters)
        self._audit_projects(issues, counters)
        self._audit_documents_and_trust(issues, counters)
        self._audit_localization(issues, counters)

        errors = [issue for issue in issues if issue.severity == "ERROR"]
        warnings = [issue for issue in issues if issue.severity == "WARN"]

        self.stdout.write(self.style.HTTP_INFO("SESCCO Production Data Audit"))
        self.stdout.write("\nRecord coverage:")
        for key in sorted(counters):
            self.stdout.write(f"- {key}: {counters[key]}")

        if issues:
            self.stdout.write("\nFindings:")
            for issue in issues:
                style = self.style.ERROR if issue.severity == "ERROR" else self.style.WARNING
                self.stdout.write(style(f"- {issue.as_line()}"))
        else:
            self.stdout.write(self.style.SUCCESS("\nNo production data issues detected."))

        self.stdout.write(
            f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s), {len(issues)} total finding(s)."
        )

        output = options.get("output")
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self._build_markdown_report(counters, issues), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Markdown report written to {path}"))

        if options.get("strict") and errors:
            raise CommandError("Production data audit failed. Fix ERROR findings or run without --strict for a report only.")

    def _audit_core(self, issues: list[AuditIssue], counters: dict[str, int]) -> None:
        counters["company_profiles"] = CompanyProfile.objects.count()
        counters["site_settings"] = SiteSettings.objects.count()
        counters["active_navigation_items"] = NavigationMenu.objects.filter(is_active=True).count()

        company = CompanyProfile.objects.first()
        if not company:
            issues.append(AuditIssue("ERROR", "Core", "Company profile is missing."))
            return

        required_company_fields = {
            "company_name": company.company_name,
            "short_name": company.short_name,
            "tagline": company.tagline,
            "description": company.description,
            "aramco_vendor_code": company.aramco_vendor_code,
            "sec_vendor_code": company.sec_vendor_code,
            "phone_primary": company.phone_primary,
            "email_primary": company.email_primary,
            "address": company.address,
            "website_url": company.website_url,
        }
        for field_name, value in required_company_fields.items():
            if self._is_blank(value):
                issues.append(AuditIssue("ERROR", "Core", f"CompanyProfile.{field_name} is empty."))

        if "dummy" in self._clean(company.description).lower() or "lorem" in self._clean(company.description).lower():
            issues.append(AuditIssue("ERROR", "Core", "Company profile still contains demo placeholder wording."))

        expected_nav = {
            "Home": "/",
            "About Us": "/about/",
            "Services": "/services/",
            "Projects": "/projects/",
            "Contact": "/contact/",
        }
        for label, url in expected_nav.items():
            if not NavigationMenu.objects.filter(title=label, url=url, is_active=True).exists():
                issues.append(AuditIssue("WARN", "Navigation", f"Expected active navigation link missing: {label} → {url}"))

    def _audit_page_content(self, issues: list[AuditIssue], counters: dict[str, int]) -> None:
        counters["published_pages"] = Page.objects.filter(is_published=True).count()
        counters["active_page_sections"] = PageSection.objects.filter(is_active=True).count()
        counters["page_faqs"] = FAQ.objects.filter(is_active=True).count()
        counters["home_highlights"] = HomeHighlight.objects.filter(is_active=True).count()
        counters["why_choose_items"] = WhyChooseItem.objects.filter(is_active=True).count()

        if not HomeHero.objects.filter(is_active=True).exists():
            issues.append(AuditIssue("ERROR", "Home", "No active HomeHero record exists."))

        about_block = HomeAboutBlock.objects.filter(is_active=True).first()
        if not about_block or self._is_blank(about_block.body):
            issues.append(AuditIssue("WARN", "Home", "Home about block should contain production copy."))

        if HomeHighlight.objects.filter(is_active=True).count() < 3:
            issues.append(AuditIssue("WARN", "Home", "At least 3 active home highlight cards are recommended."))
        if WhyChooseItem.objects.filter(is_active=True).count() < 3:
            issues.append(AuditIssue("WARN", "Home", "At least 3 active why-choose cards are recommended."))

        for page in Page.objects.filter(is_published=True):
            if self._is_blank(page.hero_title):
                issues.append(AuditIssue("WARN", "Pages", f"{page.slug}: hero_title is empty."))
            if self._is_blank(page.seo_title) or self._is_blank(page.seo_description):
                issues.append(AuditIssue("WARN", "SEO", f"{page.slug}: SEO title or description is empty."))
            if page.sections.filter(is_active=True).count() == 0 and page.template_type == "generic":
                issues.append(AuditIssue("WARN", "Pages", f"{page.slug}: generic page has no active sections."))

        for section in PageSection.objects.filter(is_active=True).select_related("page"):
            has_copy = any(
                not self._is_blank(value)
                for value in [section.title, section.subtitle, section.content, section.button_text, section.button_url]
            )
            if not has_copy and not section.image:
                issues.append(
                    AuditIssue(
                        "WARN",
                        "Page Sections",
                        f"{section.page.slug}/{section.section_type}: active section has no text, image or button content.",
                    )
                )

    def _audit_services(self, issues: list[AuditIssue], counters: dict[str, int]) -> None:
        services = Service.objects.filter(is_active=True).select_related("category")
        counters["active_service_categories"] = ServiceCategory.objects.filter(is_active=True).count()
        counters["active_services"] = services.count()
        counters["service_list_faqs"] = ServiceListFAQ.objects.filter(is_active=True).count()

        if services.count() < 6:
            issues.append(AuditIssue("WARN", "Services", "At least 6 active production services are recommended."))
        if ServiceListFAQ.objects.filter(is_active=True).count() < 4:
            issues.append(AuditIssue("WARN", "Services", "Service list page should have at least 4 FAQs."))

        for service in services:
            prefix = service.slug or service.title
            required = {
                "title": service.title,
                "short_description": service.short_description,
                "body": service.body,
                "seo_title": service.seo_title,
                "seo_description": service.seo_description,
            }
            for field_name, value in required.items():
                if self._is_blank(value):
                    issues.append(AuditIssue("WARN", "Services", f"{prefix}: {field_name} is empty."))
            if service.key_points.filter(is_active=True).count() < 2:
                issues.append(AuditIssue("WARN", "Services", f"{prefix}: add at least 2 key points."))
            if service.deliverables.filter(is_active=True).count() < 3:
                issues.append(AuditIssue("WARN", "Services", f"{prefix}: add at least 3 deliverables."))
            if service.features.filter(is_active=True).count() < 3:
                issues.append(AuditIssue("WARN", "Services", f"{prefix}: add at least 3 features."))
            if service.process_steps.filter(is_active=True).count() < 3:
                issues.append(AuditIssue("WARN", "Services", f"{prefix}: add at least 3 process steps."))
            if service.faqs.filter(is_active=True).count() < 3:
                issues.append(AuditIssue("WARN", "Services", f"{prefix}: add at least 3 service FAQs."))
            if not service.brochure:
                issues.append(AuditIssue("WARN", "Documents", f"{prefix}: service brochure file is not attached."))

    def _audit_projects(self, issues: list[AuditIssue], counters: dict[str, int]) -> None:
        projects = Project.objects.filter(is_active=True).prefetch_related("metrics", "scope_items", "documents")
        counters["active_projects"] = projects.count()
        counters["featured_projects"] = projects.filter(is_featured=True).count()
        counters["project_list_stats"] = ProjectListStat.objects.filter(is_active=True).count()

        if projects.count() < 12:
            issues.append(AuditIssue("WARN", "Projects", "At least 12 active project records are recommended for this profile."))
        if projects.filter(is_featured=True).count() < 3:
            issues.append(AuditIssue("WARN", "Projects", "At least 3 featured projects are recommended for the homepage/project list."))

        for project in projects:
            prefix = project.slug or project.title
            if self._is_blank(project.short_description):
                issues.append(AuditIssue("WARN", "Projects", f"{prefix}: short_description is empty."))
            if self._is_blank(project.summary) and self._is_blank(project.scope):
                issues.append(AuditIssue("WARN", "Projects", f"{prefix}: summary/scope content is empty."))
            if self._is_blank(project.location):
                issues.append(AuditIssue("WARN", "Projects", f"{prefix}: location is empty."))
            if self._is_blank(project.seo_title) or self._is_blank(project.seo_description):
                issues.append(AuditIssue("WARN", "SEO", f"{prefix}: project SEO title or description is empty."))
            if project.metrics.filter(is_active=True).count() < 3:
                issues.append(AuditIssue("WARN", "Projects", f"{prefix}: add at least 3 quick facts / metrics."))
            if project.scope_items.filter(is_active=True).count() < 2:
                issues.append(AuditIssue("WARN", "Projects", f"{prefix}: add at least 2 scope items."))

    def _audit_documents_and_trust(self, issues: list[AuditIssue], counters: dict[str, int]) -> None:
        docs = DownloadDocument.objects.filter(is_active=True)
        counters["active_documents"] = docs.count()
        counters["active_clients"] = Client.objects.filter(is_active=True).count()
        counters["active_partners"] = Partner.objects.filter(is_active=True).count()
        counters["active_certificates"] = Certificate.objects.filter(is_active=True).count()
        counters["active_trust_metrics"] = TrustMetric.objects.filter(is_active=True).count()

        if docs.count() < 4:
            issues.append(AuditIssue("WARN", "Documents", "At least 4 active downloadable documents are recommended."))
        for document in docs:
            if self._is_blank(document.description):
                issues.append(AuditIssue("WARN", "Documents", f"{document.title}: description is empty."))
            if not document.file:
                issues.append(AuditIssue("WARN", "Documents", f"{document.title}: file is not attached."))

        if Client.objects.filter(is_active=True).count() < 6:
            issues.append(AuditIssue("WARN", "Trust", "At least 6 active client records are recommended."))
        if Certificate.objects.filter(is_active=True).count() < 3:
            issues.append(AuditIssue("WARN", "Trust", "At least 3 active certificate records are recommended."))
        if TrustMetric.objects.filter(is_active=True).count() < 3:
            issues.append(AuditIssue("WARN", "Trust", "At least 3 trust metrics are recommended."))

    def _audit_localization(self, issues: list[AuditIssue], counters: dict[str, int]) -> None:
        active_objects = {
            "page": Page.objects.filter(is_published=True),
            "pagesection": PageSection.objects.filter(is_active=True),
            "faq": FAQ.objects.filter(is_active=True),
            "service": Service.objects.filter(is_active=True),
            "servicefaq": self._collect_related(Service.objects.filter(is_active=True), "faqs"),
            "servicefeature": self._collect_related(Service.objects.filter(is_active=True), "features"),
            "servicedeliverable": self._collect_related(Service.objects.filter(is_active=True), "deliverables"),
            "serviceprocessstep": self._collect_related(Service.objects.filter(is_active=True), "process_steps"),
            "project": Project.objects.filter(is_active=True),
            "projectmetric": self._collect_related(Project.objects.filter(is_active=True), "metrics"),
            "projectscopeitem": self._collect_related(Project.objects.filter(is_active=True), "scope_items"),
            "downloaddocument": DownloadDocument.objects.filter(is_active=True),
            "client": Client.objects.filter(is_active=True),
            "certificate": Certificate.objects.filter(is_active=True),
            "trustmetric": TrustMetric.objects.filter(is_active=True),
        }

        translated_rows = LocalizedContent.objects.filter(language_code__in=LANGUAGES)
        counters["localized_rows_ar"] = translated_rows.filter(language_code="ar").count()
        counters["localized_rows_zh_hans"] = translated_rows.filter(language_code="zh-hans").count()

        # Production-level parity check: each active object in key public content types should have at least one AR and ZH row.
        for content_type, objects in active_objects.items():
            ids = [obj.id for obj in objects]
            if not ids:
                continue
            for language in LANGUAGES:
                translated_ids = set(
                    LocalizedContent.objects.filter(
                        content_type=content_type,
                        object_id__in=ids,
                        language_code=language,
                    ).values_list("object_id", flat=True)
                )
                missing_count = len(set(ids) - translated_ids)
                if missing_count:
                    severity = "ERROR" if content_type in {"page", "service", "project"} else "WARN"
                    issues.append(
                        AuditIssue(
                            severity,
                            "Localization",
                            f"{content_type}: {missing_count} active object(s) missing {language} localization rows.",
                        )
                    )

    def _collect_related(self, queryset, related_name: str) -> list:
        items = []
        for obj in queryset.prefetch_related(related_name):
            try:
                items.extend(list(getattr(obj, related_name).filter(is_active=True)))
            except Exception:
                pass
        return items

    def _build_markdown_report(self, counters: dict[str, int], issues: list[AuditIssue]) -> str:
        errors = [issue for issue in issues if issue.severity == "ERROR"]
        warnings = [issue for issue in issues if issue.severity == "WARN"]
        lines = [
            "# SESCCO Production Data Audit",
            "",
            f"Summary: **{len(errors)} error(s)**, **{len(warnings)} warning(s)**, **{len(issues)} total finding(s)**.",
            "",
            "## Record Coverage",
            "",
        ]
        for key in sorted(counters):
            lines.append(f"- **{key}**: {counters[key]}")
        lines.extend(["", "## Findings", ""])
        if issues:
            for issue in issues:
                lines.append(f"- {issue.as_line()}")
        else:
            lines.append("No production data issues detected.")
        lines.extend(
            [
                "",
                "## Recommended command sequence",
                "",
                "```bash",
                "python manage.py migrate",
                "python manage.py seed_sescco_production --run-audit",
                "python manage.py production_data_audit --strict --output reports/production-data-audit.md",
                "python manage.py collectstatic --noinput",
                "```",
                "",
            ]
        )
        return "\n".join(lines)

    def _is_blank(self, value) -> bool:
        return not self._clean(value)

    def _clean(self, value) -> str:
        if value is None:
            return ""
        return strip_tags(str(value)).replace("&nbsp;", " ").strip()
