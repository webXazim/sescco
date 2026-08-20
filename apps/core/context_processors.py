from django.conf import settings
from django.core.cache import cache

from .models import (
    BusinessHour, CompanyProfile, ContactMethod, CTASection, CTASettings,
    FooterColumn, NavigationMenu, OfficeLocation, SiteSettings, SocialLink,
    ThemeSettings, TrustMetric
)


def _first_or_new(model):
    obj = model.objects.first()
    return obj or model()


def _language_urls(request):
    path = request.path or "/"
    known_prefixes = ["/ar", "/zh-hans", "/en"]

    clean_path = path
    for prefix in known_prefixes:
        if clean_path == prefix:
            clean_path = "/"
            break
        if clean_path.startswith(prefix + "/"):
            clean_path = clean_path[len(prefix):] or "/"
            break

    if not clean_path.startswith("/"):
        clean_path = "/" + clean_path

    # Canonical and hreflang alternates should point to the stable page URL,
    # not to filtered/search query variants that can create duplicate index entries.
    return {
        "en": clean_path,
        "ar": ("/ar" + clean_path if clean_path != "/" else "/ar/"),
        "zh_hans": ("/zh-hans" + clean_path if clean_path != "/" else "/zh-hans/"),
    }


def _absolute_language_urls(request, language_urls):
    return {key: request.build_absolute_uri(value) for key, value in language_urls.items()}


def _footer_map_context():
    """Return the same Google map data used by the Contact page for the footer.

    Kept defensive because core context is loaded on every page, including admin.
    If the inquiries app is temporarily unavailable during migrations, the footer
    simply hides the mini map instead of breaking the site.
    """
    primary_office = OfficeLocation.objects.filter(is_active=True).order_by("-is_primary", "sort_order", "id").first()
    try:
        from apps.inquiries.models import ContactPageSettings

        contact_settings = ContactPageSettings.objects.first()
    except Exception:
        contact_settings = None

    embed_url = ""
    directions_url = ""
    if contact_settings:
        embed_url = contact_settings.google_map_embed_url or ""
        directions_url = contact_settings.google_map_url or ""

    if primary_office:
        embed_url = embed_url or primary_office.map_embed_url or ""
        directions_url = directions_url or primary_office.map_url or ""

    return {
        "footer_primary_office": primary_office,
        "footer_map_embed_url": embed_url,
        "footer_map_url": directions_url,
    }


def site_context(request):
    language_urls = _language_urls(request)
    canonical_url = request.build_absolute_uri(request.path)
    cache_key = "site-context:v1"
    shared_context = cache.get(cache_key)
    if shared_context is None:
        shared_context = {
            "company": _first_or_new(CompanyProfile),
            "site_settings": _first_or_new(SiteSettings),
            "theme": _first_or_new(ThemeSettings),
            "cta_settings": _first_or_new(CTASettings),
            "global_cta": CTASection.objects.filter(key="global-main", is_active=True).first(),
            "nav_items": list(NavigationMenu.objects.filter(is_active=True)),
            "footer_columns": list(FooterColumn.objects.filter(is_active=True).prefetch_related("links")),
            "social_links": list(SocialLink.objects.filter(is_active=True)),
            "trust_metrics_global": list(TrustMetric.objects.filter(is_active=True)),
            "office_locations": list(OfficeLocation.objects.filter(is_active=True)),
            "business_hours": list(BusinessHour.objects.filter(is_active=True)),
            "contact_methods": list(ContactMethod.objects.filter(is_active=True)),
            **_footer_map_context(),
        }
        cache.set(cache_key, shared_context, settings.SITE_CONTEXT_CACHE_SECONDS)

    return {
        **shared_context,
        "language_urls": language_urls,
        "absolute_language_urls": _absolute_language_urls(request, language_urls),
        "canonical_url": canonical_url,
    }
