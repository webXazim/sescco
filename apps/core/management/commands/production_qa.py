from django.core.management.base import BaseCommand
from apps.clients.models import Certificate, Client, Partner
from apps.core.models import CompanyProfile, NavigationMenu, TrustMetric
from apps.documents.models import DownloadDocument
from apps.pages.models import HomeHighlight, HomeHero, Page
from apps.projects.models import Project
from apps.services.models import Service


class Command(BaseCommand):
    help = "Run SESCCO production readiness checks for logo, CMS data and non-demo content."

    def handle(self, *args, **options):
        issues = []

        company = CompanyProfile.objects.first()
        if not company:
            issues.append("CompanyProfile is missing.")
        else:
            if not company.logo:
                issues.append("CompanyProfile.logo is empty. Static fallback works, but CMS logo should be set.")
            if "Summit" not in company.company_name and "SESCCO" not in company.short_name:
                issues.append("Company identity does not look SESCCO-specific.")
            if not company.aramco_vendor_code:
                issues.append("ARAMCO vendor code is missing.")
            if not company.sec_vendor_code:
                issues.append("SEC vendor code is missing.")

        expected_nav = ["Home", "About Us", "Services", "Projects", "Certificates", "Careers", "Contact"]
        for item in expected_nav:
            if not NavigationMenu.objects.filter(title=item, is_active=True).exists():
                issues.append(f"Navigation item missing or inactive: {item}")

        if not HomeHero.objects.filter(is_active=True).exists():
            issues.append("Active HomeHero is missing.")
        if HomeHighlight.objects.filter(title__in=["CMS", "CRUD", "Admin Editable"]).exists() or HomeHighlight.objects.filter(value__in=["CMS", "CRUD", "Admin Editable", "Project Ready"]).exists():
            issues.append("Generic demo home highlight still exists: CMS/CRUD/Admin Editable/Project Ready.")
        if HomeHighlight.objects.count() < 3:
            issues.append("Home highlights should have at least 3 production cards.")

        counts = {
            "Published pages": Page.objects.filter(is_published=True).count(),
            "Services": Service.objects.filter(is_active=True).count(),
            "Projects": Project.objects.filter(is_active=True).count(),
            "Clients": Client.objects.filter(is_active=True).count(),
            "Partners": Partner.objects.filter(is_active=True).count(),
            "Certificates": Certificate.objects.filter(is_active=True).count(),
            "Documents": DownloadDocument.objects.filter(is_active=True).count(),
            "Trust metrics": TrustMetric.objects.filter(is_active=True).count(),
        }

        self.stdout.write(self.style.HTTP_INFO("SESCCO Production Readiness Report"))
        for label, count in counts.items():
            self.stdout.write(f"{label:20}: {count}")
            if count == 0:
                issues.append(f"{label} has no active records.")

        if issues:
            self.stdout.write(self.style.WARNING("\nIssues to review:"))
            for issue in issues:
                self.stdout.write(f"- {issue}")
        else:
            self.stdout.write(self.style.SUCCESS("\nProduction readiness checks passed."))

        self.stdout.write("\nManual A-Z page checks:")
        for url in ["/", "/about/", "/services/", "/projects/", "/clients-certifications/", "/careers/", "/contact/", "/ar/", "/zh-hans/"]:
            self.stdout.write(f"- {url}")
