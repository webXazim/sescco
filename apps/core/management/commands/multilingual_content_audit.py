from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError
from django.db import models
from django.utils.html import strip_tags

from apps.careers.models import CareerBenefit, CareerDepartment, CareerPageSettings, CareerProcessStep, CareerStat, JobOpening
from apps.clients.models import Accreditation, Certificate, CertificateCategory, Client, ClientCategory, ComplianceBlock, Partner, Standard, TrustPageSettings
from apps.core.models import CompanyProfile, CTASettings, FooterColumn, FooterLink, LocalizedContent, NavigationMenu, TrustMetric
from apps.documents.models import DocumentCategory, DocumentPageCTA, DownloadDocument, DownloadsPageSettings
from apps.inquiries.models import ContactPageSettings, InquirySubject
from apps.pages.models import (
    AboutPageSettings,
    FAQ,
    HomeAboutBlock,
    HomeHero,
    HomeHighlight,
    HomeSectionSettings,
    LeadershipMessage,
    MissionVisionItem,
    Page,
    PageSection,
    TimelineItem,
    ValueItem,
    WhyChooseItem,
)
from apps.projects.models import Project, ProjectCategory, ProjectCTA, ProjectListPageSettings, ProjectListStat, ProjectMetric, ProjectScopeItem
from apps.services.models import (
    Service,
    ServiceCategory,
    ServiceCTA,
    ServiceDeliverable,
    ServiceFAQ,
    ServiceFeature,
    ServiceKeyPoint,
    ServiceListFAQ,
    ServiceListPageSettings,
    ServiceListProcessStep,
    ServiceProcessStep,
)


LANGUAGES = ("ar", "zh-hans")
ARABIC_RE = re.compile(r"[\u0600-\u06FF]")
CJK_RE = re.compile(r"[\u3400-\u9FFF]")
LATIN_RE = re.compile(r"[A-Za-z]")
TOKEN_RE = re.compile(r"{{.*?}}|{%.*?%}|https?://|www\.|@")

# Field names that are allowed to remain English/code-like because they are brand names,
# URLs, email addresses, template variables, or compact SEO identifiers.
ALLOW_LATIN_HEAVY_FIELDS = {
    "short_name",
    "code",
    "vendor_code",
    "aramco_vendor_code",
    "sec_vendor_code",
    "email",
    "email_primary",
    "email_secondary",
    "website_url",
    "button_url",
    "url",
    "slug",
    "icon_text",
    "salary_range",
}
ALLOW_LATIN_TITLES = {
    "SESCCO",
    "ARAMCO",
    "SEC",
    "GIS",
    "HVAC",
    "MEP",
    "MV",
    "LV",
    "SWGR",
    "RTR",
    "EPCC",
    "Saudi Aramco",
    "Saudi Electricity Company",
    "Saudi Water Company",
}

# Proper nouns are expected to remain Latin in Arabic/Chinese.
# Client names, partner names, certificate names, document filenames/titles,
# vendor/accreditation labels, and some metric values often have no meaningful
# translation. They should not block deployment in strict mode.
PROPER_NOUN_ROW_FIELDS = {
    ("client", "name"),
    ("partner", "name"),
    ("accreditation", "name"),
    ("standard", "name"),
    ("certificate", "name"),
    ("certificate", "title"),
    ("clientcategory", "name"),
    ("certificatecategory", "name"),
    ("projectmetric", "value"),
    ("projectmetric", "label"),
    ("downloaddocument", "file"),
}

# These fields can legitimately be reused when they contain project names,
# client names, standards, product codes, or short labels. Exact-copy findings
# here are warnings, not strict deployment blockers.
EXACT_COPY_WARNING_FIELDS = {"name", "title", "label", "value", "location", "client", "contractor", "end_client", "status"}

# Project references contain many contract titles, facilities, voltage levels, vendor names,
# client names, locations, and technical abbreviations. A project row that still has an
# English-looking title/scope should be surfaced for human QA, but it should not block
# the strict launch gate after seeded Arabic/Chinese descriptive data exists.
EXACT_COPY_WARNING_CONTENT_TYPES = {
    "project",
    "projectscopeitem",
    "projectmetric",
    "client",
    "partner",
    "certificate",
    "downloaddocument",
}

CONTENT_MODEL_MAP = {
    cls.__name__.lower(): cls
    for cls in [
        CompanyProfile,
        NavigationMenu,
        FooterColumn,
        FooterLink,
        CTASettings,
        TrustMetric,
        HomeHero,
        HomeAboutBlock,
        HomeSectionSettings,
        HomeHighlight,
        AboutPageSettings,
        MissionVisionItem,
        ValueItem,
        LeadershipMessage,
        TimelineItem,
        FAQ,
        WhyChooseItem,
        Page,
        PageSection,
        ServiceCategory,
        Service,
        ServiceListPageSettings,
        ServiceListProcessStep,
        ServiceListFAQ,
        ServiceKeyPoint,
        ServiceDeliverable,
        ServiceProcessStep,
        ServiceFeature,
        ServiceFAQ,
        ServiceCTA,
        ProjectCategory,
        Project,
        ProjectListPageSettings,
        ProjectListStat,
        ProjectMetric,
        ProjectCTA,
        ProjectScopeItem,
        TrustPageSettings,
        Client,
        Partner,
        Certificate,
        ClientCategory,
        CertificateCategory,
        Accreditation,
        Standard,
        ComplianceBlock,
        DownloadsPageSettings,
        DownloadDocument,
        DocumentPageCTA,
        DocumentCategory,
        CareerPageSettings,
        CareerStat,
        CareerBenefit,
        CareerProcessStep,
        CareerDepartment,
        JobOpening,
        ContactPageSettings,
        InquirySubject,
    ]
}


class Finding:
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
    help = "Audit Arabic and Chinese CMS localization quality, not only row coverage."

    def add_arguments(self, parser):
        parser.add_argument("--strict", action="store_true", help="Fail when blocking translation issues are found.")
        parser.add_argument("--output", default="", help="Optional Markdown report path, e.g. reports/multilingual-content-audit.md.")
        parser.add_argument(
            "--sample-limit",
            type=int,
            default=80,
            help="Maximum number of row-level findings to print/write before summarizing the rest.",
        )

    def handle(self, *args, **options):
        findings: list[Finding] = []
        counters: dict[str, int] = defaultdict(int)
        self._audit_rows(findings, counters, options["sample_limit"])
        self._audit_parity(findings, counters)

        errors = [f for f in findings if f.severity == "ERROR"]
        warnings = [f for f in findings if f.severity == "WARN"]

        self.stdout.write(self.style.HTTP_INFO("SESCCO Multilingual Content Accuracy Audit"))
        self.stdout.write("\nRecord coverage:")
        for key in sorted(counters):
            self.stdout.write(f"- {key}: {counters[key]}")

        if findings:
            self.stdout.write("\nFindings:")
            for finding in findings[: options["sample_limit"]]:
                style = self.style.ERROR if finding.severity == "ERROR" else self.style.WARNING
                self.stdout.write(style(f"- {finding.as_line()}"))
            if len(findings) > options["sample_limit"]:
                self.stdout.write(self.style.WARNING(f"- ... {len(findings) - options['sample_limit']} additional finding(s) hidden by sample limit."))
        else:
            self.stdout.write(self.style.SUCCESS("\nNo multilingual content accuracy issues detected."))

        self.stdout.write(
            f"\nSummary: {len(errors)} error(s), {len(warnings)} warning(s), {len(findings)} total finding(s)."
        )

        output = options.get("output")
        if output:
            path = Path(output)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(self._build_report(counters, findings, options["sample_limit"]), encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Markdown report written to {path}"))

        if options.get("strict") and errors:
            raise CommandError("Multilingual content audit failed. Fix ERROR findings or run without --strict for a report only.")

    def _audit_rows(self, findings: list[Finding], counters: dict[str, int], sample_limit: int) -> None:
        rows = LocalizedContent.objects.filter(language_code__in=LANGUAGES).order_by("content_type", "object_id", "language_code", "field_name")
        counters["localized_rows_total"] = rows.count()
        counters["localized_rows_ar"] = rows.filter(language_code="ar").count()
        counters["localized_rows_zh_hans"] = rows.filter(language_code="zh-hans").count()

        for row in rows:
            counters[f"rows_{row.content_type}"] += 1
            translated = self._clean(row.text)
            if not translated:
                findings.append(Finding("ERROR", "Localization", self._row_label(row, "translated text is empty.")))
                continue

            lower = translated.lower()
            if any(marker in lower for marker in ["lorem ipsum", "translation:", "ترجمة:", "翻译:", "todo", "placeholder"]):
                findings.append(Finding("ERROR", "Localization", self._row_label(row, "demo/placeholder wording remains.")))

            source = self._get_source_text(row)
            source_clean = self._clean(source)
            if source_clean and self._looks_like_exact_copy(source_clean, translated, row.field_name):
                severity = "WARN" if self._is_exact_copy_warning_row(row, translated) else "ERROR"
                findings.append(Finding(severity, "Localization", self._row_label(row, "translation appears to be an exact English copy.")))

            if source_clean and len(source_clean) > 80 and len(translated) < max(18, len(source_clean) * 0.16):
                findings.append(Finding("WARN", "Localization", self._row_label(row, "translation is suspiciously short compared with English source.")))

            if row.language_code == "ar":
                self._audit_arabic_row(row, translated, findings)
            elif row.language_code == "zh-hans":
                self._audit_chinese_row(row, translated, findings)

    def _audit_arabic_row(self, row: LocalizedContent, text: str, findings: list[Finding]) -> None:
        if self._is_exempt_field(row.field_name, text) or self._is_proper_noun_row(row, text):
            return
        has_arabic = bool(ARABIC_RE.search(text))
        latin_ratio = self._latin_ratio(text)
        if not has_arabic and len(text) > 12:
            findings.append(Finding("WARN", "Arabic", self._row_label(row, "Arabic row has no Arabic characters.")))
        elif latin_ratio > 0.55 and len(text) > 35 and not self._mostly_allowed_terms(text):
            findings.append(Finding("WARN", "Arabic", self._row_label(row, "Arabic row is Latin-heavy and may be untranslated.")))

    def _audit_chinese_row(self, row: LocalizedContent, text: str, findings: list[Finding]) -> None:
        if self._is_exempt_field(row.field_name, text) or self._is_proper_noun_row(row, text):
            return
        has_cjk = bool(CJK_RE.search(text))
        latin_ratio = self._latin_ratio(text)
        if not has_cjk and len(text) > 12:
            findings.append(Finding("WARN", "Chinese", self._row_label(row, "Chinese row has no Chinese characters.")))
        elif latin_ratio > 0.55 and len(text) > 35 and not self._mostly_allowed_terms(text):
            findings.append(Finding("WARN", "Chinese", self._row_label(row, "Chinese row is Latin-heavy and may be untranslated.")))

    def _audit_parity(self, findings: list[Finding], counters: dict[str, int]) -> None:
        # Field-level parity: for active public content, AR/ZH should translate the fields that exist in English.
        required_public_types = {
            "companyprofile",
            "navigationmenu",
            "page",
            "pagesection",
            "faq",
            "homehero",
            "homeaboutblock",
            "homehighlight",
            "service",
            "servicefaq",
            "servicefeature",
            "servicedeliverable",
            "serviceprocessstep",
            "project",
            "projectmetric",
            "projectscopeitem",
            "downloaddocument",
            "client",
            "certificate",
            "trustmetric",
            "contactpagesettings",
            "careerpagesettings",
            "jobopening",
        }
        for content_type in required_public_types:
            model = CONTENT_MODEL_MAP.get(content_type)
            if not model:
                continue
            objects = self._active_queryset(model)
            for obj in objects:
                fields = self._source_text_fields(obj)
                if not fields:
                    continue
                for language in LANGUAGES:
                    translated_fields = set(
                        LocalizedContent.objects.filter(
                            content_type=content_type,
                            object_id=obj.id,
                            language_code=language,
                            field_name__in=fields,
                        ).values_list("field_name", flat=True)
                    )
                    missing = sorted(set(fields) - translated_fields)
                    if missing:
                        counters[f"missing_field_rows_{language}"] += len(missing)
                        severity = "ERROR" if content_type in {"page", "service", "companyprofile"} else "WARN"
                        sample = ", ".join(missing[:5])
                        more = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
                        findings.append(
                            Finding(
                                severity,
                                "Field Parity",
                                f"{content_type}:{obj.id} missing {language} translation for: {sample}{more}.",
                            )
                        )

    def _active_queryset(self, model: type[models.Model]):
        qs = model.objects.all()
        if any(field.name == "is_active" for field in model._meta.fields):
            qs = qs.filter(is_active=True)
        if any(field.name == "is_published" for field in model._meta.fields):
            qs = qs.filter(is_published=True)
        return qs

    def _source_text_fields(self, obj: models.Model) -> list[str]:
        ignored = {"id", "created_at", "updated_at", "sort_order", "is_active", "is_published"}
        fields: list[str] = []
        for field in obj._meta.fields:
            if field.name in ignored:
                continue
            if isinstance(field, (models.CharField, models.TextField)):
                value = getattr(obj, field.name, "")
                if self._clean(value) and not self._is_exempt_field(field.name, self._clean(value)):
                    fields.append(field.name)
        return fields

    def _get_source_text(self, row: LocalizedContent) -> str:
        model = CONTENT_MODEL_MAP.get(row.content_type)
        if not model:
            return ""
        try:
            obj = model.objects.get(id=row.object_id)
        except model.DoesNotExist:
            return ""
        return getattr(obj, row.field_name, "")

    def _build_report(self, counters: dict[str, int], findings: list[Finding], sample_limit: int) -> str:
        errors = [f for f in findings if f.severity == "ERROR"]
        warnings = [f for f in findings if f.severity == "WARN"]
        lines = [
            "# SESCCO Multilingual Content Accuracy Audit",
            "",
            f"Summary: **{len(errors)} error(s)**, **{len(warnings)} warning(s)**, **{len(findings)} total finding(s)**.",
            "",
            "## Coverage",
            "",
        ]
        for key in sorted(counters):
            lines.append(f"- **{key}**: {counters[key]}")
        lines.extend(["", "## Findings", ""])
        if findings:
            for finding in findings[:sample_limit]:
                lines.append(f"- {finding.as_line()}")
            if len(findings) > sample_limit:
                lines.append(f"- ... {len(findings) - sample_limit} additional finding(s) hidden by sample limit.")
        else:
            lines.append("No multilingual content accuracy issues detected.")
        lines.extend(
            [
                "",
                "## Recommended command sequence",
                "",
                "```bash",
                "python manage.py migrate",
                "python manage.py seed_sescco_production --run-audit --run-language-audit --run-asset-audit",
                "python manage.py multilingual_content_audit --strict --output reports/multilingual-content-audit.md",
                "python manage.py collectstatic --noinput",
                "```",
                "",
            ]
        )
        return "\n".join(lines)

    def _row_label(self, row: LocalizedContent, message: str) -> str:
        return f"{row.content_type}:{row.object_id}:{row.language_code}:{row.field_name} — {message}"

    def _clean(self, value: Any) -> str:
        if value is None:
            return ""
        text = strip_tags(str(value)).replace("&nbsp;", " ")
        return re.sub(r"\s+", " ", text).strip()

    def _norm(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", self._clean(text).lower())

    def _looks_like_exact_copy(self, source: str, translated: str, field_name: str) -> bool:
        if self._is_exempt_field(field_name, translated):
            return False
        if len(source) < 18 or len(translated) < 18:
            return False
        return self._norm(source) == self._norm(translated)

    def _latin_ratio(self, text: str) -> float:
        visible = re.sub(r"\s+", "", TOKEN_RE.sub("", text))
        if not visible:
            return 0.0
        latin_count = len(LATIN_RE.findall(visible))
        return latin_count / max(len(visible), 1)

    def _is_exempt_field(self, field_name: str, text: str) -> bool:
        lower_field = field_name.lower()
        if any(key in lower_field for key in ALLOW_LATIN_HEAVY_FIELDS):
            return True
        if TOKEN_RE.search(text):
            return True
        if len(text) <= 8:
            return True
        if text in ALLOW_LATIN_TITLES:
            return True
        # Values that are almost entirely numbers/symbols are not human-language content.
        letters = re.findall(r"[A-Za-z\u0600-\u06FF\u3400-\u9FFF]", text)
        return len(letters) <= 2

    def _is_proper_noun_row(self, row: LocalizedContent, text: str) -> bool:
        field = row.field_name.lower()
        content_type = row.content_type.lower()
        if (content_type, field) in PROPER_NOUN_ROW_FIELDS:
            return True
        if field in {"name", "value"} and self._mostly_allowed_terms(text):
            return True
        return False

    def _is_exact_copy_warning_row(self, row: LocalizedContent, text: str) -> bool:
        field = row.field_name.lower()
        content_type = row.content_type.lower()
        if self._is_proper_noun_row(row, text):
            return True
        if content_type in EXACT_COPY_WARNING_CONTENT_TYPES:
            return True
        if field in EXACT_COPY_WARNING_FIELDS and self._mostly_allowed_terms(text):
            return True
        return False

    def _mostly_allowed_terms(self, text: str) -> bool:
        cleaned = text
        for term in ALLOW_LATIN_TITLES:
            cleaned = cleaned.replace(term, "")
        cleaned = TOKEN_RE.sub("", cleaned)
        return self._latin_ratio(cleaned) < 0.35
