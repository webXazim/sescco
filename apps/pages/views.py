from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from apps.clients.models import Certificate, Client
from apps.documents.models import DownloadDocument
from apps.projects.models import Project
from apps.services.models import Service
from .models import AboutPageSettings, GenericPageSettings, HomeAboutBlock, HomeHero, HomeHeroSphereCard, HomeHighlight, HomeSectionSettings, LeadershipMessage, Page, WhyChooseItem


def _page_meta(page, fallback_title, fallback_description=""):
    if not page:
        return {"meta_title": fallback_title, "meta_description": fallback_description}
    return {
        "meta_title": page.seo_title or page.title or fallback_title,
        "meta_description": page.seo_description or page.hero_subtitle or fallback_description,
        "meta_image_url": page.og_image.url if getattr(page, "og_image", None) else (page.hero_image.url if getattr(page, "hero_image", None) else ""),
    }



def _home_sphere_cards_json():
    cards = []
    for card in HomeHeroSphereCard.objects.filter(is_active=True, is_featured=True, card_type="image").order_by("sort_order", "id")[:18]:
        image_url = ""
        if card.image:
            image_url = card.image.url
        elif card.static_image_path:
            image_url = static(card.static_image_path)

        if not image_url:
            # Avoid broken image cards. The sphere now uses visual cards only;
            # text/data cards are intentionally excluded from the home hero.
            continue

        cards.append({
            "type": "image",
            "src": image_url,
            "title": card.title,
            "sub": "",
            "big": "",
            "alt": card.alt_text or card.title,
        })
    return cards


def home(request):
    page = Page.objects.filter(template_type="home", is_published=True).first()
    home_settings = HomeSectionSettings.objects.first() or HomeSectionSettings()
    services_limit = home_settings.services_limit or 6
    projects_limit = home_settings.projects_limit or 4
    clients_limit = home_settings.clients_limit or 6
    # Home should preview a maximum of six certificates. If more exist, the template shows a
    # clear View more link to the complete certificates section on the Clients page.
    certificates_limit = 6
    total_active_certificates = Certificate.objects.filter(is_active=True).count()

    featured_certificates = list(
        Certificate.objects.filter(is_active=True, is_featured=True)
        .order_by("sort_order", "id")[:certificates_limit]
    )
    if len(featured_certificates) < certificates_limit:
        seen_ids = [certificate.id for certificate in featured_certificates]
        fallback_certificates = Certificate.objects.filter(is_active=True).exclude(id__in=seen_ids).order_by("sort_order", "id")[: max(certificates_limit - len(featured_certificates), 0)]
        featured_certificates.extend(list(fallback_certificates))

    context = {
        "page": page,
        "home_hero": HomeHero.objects.filter(is_active=True).first(),
        "home_sphere_cards_json": _home_sphere_cards_json(),
        "home_about": HomeAboutBlock.objects.filter(is_active=True).first(),
        "home_settings": home_settings,
        "home_highlights": HomeHighlight.objects.filter(is_active=True),
        "why_choose_items": WhyChooseItem.objects.filter(is_active=True, show_on_home=True),
        "home_leadership_message": LeadershipMessage.objects.filter(is_active=True).order_by("sort_order", "id").first(),
        "featured_services": Service.objects.filter(is_active=True, is_featured=True)[:services_limit],
        "featured_projects": Project.objects.filter(is_active=True, is_featured=True)[:projects_limit],
        "featured_clients": list(Client.objects.filter(is_active=True, is_featured=True).order_by("sort_order", "id")) or list(Client.objects.filter(is_active=True).order_by("sort_order", "id")[:max(clients_limit, 8)]),
        "featured_certificates": featured_certificates,
        "home_certificates_has_more": total_active_certificates > certificates_limit,
        "featured_documents": DownloadDocument.objects.filter(is_active=True, is_featured=True)[:4],
        **_page_meta(page, "SESCCO | Engineering & Contracting Services", "Engineering, civil, fitout and contract support services in Saudi Arabia."),
    }
    return render(request, "pages/home.html", context)


def about(request):
    page = Page.objects.filter(template_type="about", is_published=True).first()
    about_settings = None
    if page:
        about_settings = getattr(page, "about_settings", None)
    if about_settings is None:
        about_settings = AboutPageSettings()

    leadership_message = None
    if getattr(about_settings, "show_leadership", False):
        if page:
            leadership_message = LeadershipMessage.objects.filter(is_active=True, page=page).order_by("sort_order", "id").first()
        if leadership_message is None:
            leadership_message = LeadershipMessage.objects.filter(is_active=True, page__isnull=True).order_by("sort_order", "id").first()
        if leadership_message is None:
            leadership_message = LeadershipMessage.objects.filter(is_active=True).order_by("sort_order", "id").first()

    context = {
        "page": page,
        "about_settings": about_settings,
        "why_choose_items": WhyChooseItem.objects.filter(is_active=True, show_on_about=True),
        "leadership_message": leadership_message,
        **_page_meta(page, "About SESCCO", "Company profile, mission, vision, capabilities and leadership message."),
    }
    return render(request, "pages/about.html", context)


def generic_page(request, slug):
    page = get_object_or_404(Page, slug=slug, is_published=True)
    generic_settings = getattr(page, "generic_settings", None)
    if generic_settings is None:
        generic_settings = GenericPageSettings(page=page)
    return render(request, "pages/generic.html", {"page": page, "generic_settings": generic_settings, **_page_meta(page, page.title, page.hero_subtitle)})


def error_404(request, exception):
    return render(request, "errors/404.html", status=404)


def error_500(request):
    return render(request, "errors/500.html", status=500)
