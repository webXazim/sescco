from django.core.management.base import BaseCommand
from apps.core.models import CompanyProfile, NavigationMenu
from apps.pages.models import HomeHero, Page
from apps.services.models import Service
from apps.projects.models import Project
from apps.clients.models import Client, Certificate
from apps.documents.models import DownloadDocument
from apps.inquiries.models import InquirySubject


class Command(BaseCommand):
    help = "Check important CMS records after setup."

    def handle(self, *args, **options):
        checks = [
            ("Company Profile", CompanyProfile.objects.exists()),
            ("Navigation Menu", NavigationMenu.objects.exists()),
            ("Home Page", Page.objects.filter(template_type="home").exists()),
            ("About Page", Page.objects.filter(template_type="about").exists()),
            ("Home Hero", HomeHero.objects.exists()),
            ("Services", Service.objects.exists()),
            ("Projects", Project.objects.exists()),
            ("Clients", Client.objects.exists()),
            ("Certificates", Certificate.objects.exists()),
            ("Documents", DownloadDocument.objects.exists()),
            ("Inquiry Subjects", InquirySubject.objects.exists()),
        ]
        ok = True
        for label, passed in checks:
            if passed:
                self.stdout.write(self.style.SUCCESS(f"✓ {label}"))
            else:
                ok = False
                self.stdout.write(self.style.WARNING(f"⚠ Missing: {label}"))
        if ok:
            self.stdout.write(self.style.SUCCESS("CMS check passed."))
        else:
            self.stdout.write(self.style.WARNING("CMS check completed with missing optional/required seed data. Run: python manage.py seed_site"))
