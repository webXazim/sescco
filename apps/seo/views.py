from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.utils.html import escape
from django.utils.timezone import now
from apps.clients.models import Client
from apps.documents.models import DownloadDocument
from apps.pages.models import Page
from apps.projects.models import Project
from apps.services.models import Service
from .models import RobotsSettings


LANGUAGE_PREFIXES = {
    "en": "",
    "ar": "/ar",
    "zh-Hans": "/zh-hans",
}


def _absolute(request, path):
    clean = path if path.startswith("/") else "/" + path
    return request.build_absolute_uri(clean)


def _localized_path(path, language_code):
    clean = path if path.startswith("/") else "/" + path
    prefix = LANGUAGE_PREFIXES.get(language_code, "")
    if not prefix:
        return clean
    return prefix + clean if clean != "/" else prefix + "/"


def robots_txt(request):
    settings = RobotsSettings.objects.first()
    if settings and settings.content:
        content = settings.content
        # Keep old seeded robots settings working, but make sitemap URLs absolute for crawlers.
        content = content.replace("Sitemap: /sitemap.xml", f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}")
        content = content.replace("Sitemap: /localized-sitemap.xml", f"Sitemap: {request.build_absolute_uri('/localized-sitemap.xml')}")
    else:
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}\n"
            f"Sitemap: {request.build_absolute_uri('/localized-sitemap.xml')}"
        )
    return HttpResponse(content, content_type="text/plain")


def localized_sitemap(request):
    """Multilingual sitemap with hreflang alternates for English, Arabic and Chinese."""
    entries = []

    def add(path, priority="0.70", changefreq="weekly", lastmod=None):
        clean = path if path.startswith("/") else "/" + path
        if not any(existing["path"] == clean for existing in entries):
            entries.append({
                "path": clean,
                "priority": priority,
                "changefreq": changefreq,
                "lastmod": lastmod,
            })

    add("/", "1.00", "weekly")
    for name, priority in [
        ("about", "0.85"),
        ("service_list", "0.90"),
        ("project_list", "0.90"),
        ("clients_certifications", "0.75"),
        ("downloads", "0.75"),
        ("career_list", "0.70"),
        ("contact", "0.85"),
    ]:
        try:
            add(reverse(name), priority, "weekly")
        except Exception:
            pass

    for page in Page.objects.filter(is_published=True).exclude(template_type__in=["home", "about"]):
        try:
            add(reverse("generic_page", kwargs={"slug": page.slug}), "0.65", "monthly", page.updated_at)
        except Exception:
            pass
    for service in Service.objects.filter(is_active=True):
        try:
            add(service.get_absolute_url(), "0.80", "monthly", service.updated_at)
        except Exception:
            pass
    for project in Project.objects.filter(is_active=True):
        try:
            add(project.get_absolute_url(), "0.78", "monthly", project.updated_at)
        except Exception:
            pass
    # Documents share the downloads page, but including it above helps discovery without duplicating every file URL.

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    for entry in entries:
        default_loc = _absolute(request, _localized_path(entry["path"], "en"))
        lines.append("  <url>")
        lines.append(f"    <loc>{escape(default_loc)}</loc>")
        for lang in ["en", "ar", "zh-Hans"]:
            href = _absolute(request, _localized_path(entry["path"], lang))
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{escape(href)}" />')
        lines.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{escape(default_loc)}" />')
        if entry.get("lastmod"):
            lines.append(f"    <lastmod>{entry['lastmod'].date().isoformat()}</lastmod>")
        lines.append(f"    <changefreq>{entry['changefreq']}</changefreq>")
        lines.append(f"    <priority>{entry['priority']}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return HttpResponse("\n".join(lines), content_type="application/xml")


def healthz(request):
    """Lightweight deployment health endpoint for load balancers and uptime monitors."""
    response = JsonResponse({"status": "ok", "service": "sescco", "ready": True})
    response["Cache-Control"] = "no-store, max-age=0"
    return response
