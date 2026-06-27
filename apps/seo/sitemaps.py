from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from django.utils import timezone
from django.urls import reverse
from apps.documents.models import DownloadDocument
from apps.careers.models import JobOpening
from apps.pages.models import Page
from apps.projects.models import Project
from apps.services.models import Service


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["home", "about", "service_list", "project_list", "clients_certifications", "career_list", "contact"]

    def location(self, item):
        return reverse(item)


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Page.objects.filter(is_published=True).exclude(template_type__in=["home", "about"])

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("generic_page", kwargs={"slug": obj.slug})


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Project.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class DocumentSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return DownloadDocument.objects.filter(is_active=True, is_public=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("downloads")


class CareerSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        today = timezone.localdate()
        return JobOpening.objects.filter(is_active=True, status="published").filter(Q(application_deadline__isnull=True) | Q(application_deadline__gte=today))

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("job_detail", kwargs={"slug": obj.slug})
