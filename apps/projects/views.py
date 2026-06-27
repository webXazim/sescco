from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from .models import Project, ProjectCategory, ProjectDetailPageSettings, ProjectListPageSettings, ProjectListStat
from apps.clients.models import Client
from apps.core.models import CompanyProfile


def _image_url(image_field):
    if not image_field:
        return ""
    try:
        return image_field.url
    except ValueError:
        return ""


def _client_logo_url_by_name(name):
    if not name:
        return ""
    clean_name = name.strip()
    if not clean_name:
        return ""

    logo_clients = Client.objects.filter(is_active=True, logo__isnull=False).exclude(logo="")
    client = logo_clients.filter(name__iexact=clean_name).first()
    if not client and len(clean_name) > 3:
        client = logo_clients.filter(Q(name__icontains=clean_name) | Q(description__icontains=clean_name)).first()
    return _image_url(client.logo) if client else ""


def _company_logo_url_by_name(name):
    if not name:
        return ""
    company = CompanyProfile.objects.first()
    if not company:
        return ""

    clean_name = name.strip().lower()
    company_names = [company.short_name, company.company_name]
    is_company = any(
        company_name and (company_name.lower() in clean_name or clean_name in company_name.lower())
        for company_name in company_names
    )
    if not is_company:
        return ""
    return _image_url(company.logo) or static("img/brand/sescco-logo.svg")


def _stakeholder_logo_url(project, relation_field, legacy_logo_field, name_field, include_company=False):
    stakeholder = getattr(project, relation_field, None)
    if stakeholder:
        logo_url = _image_url(stakeholder.logo)
        if logo_url:
            return logo_url

    logo_url = _image_url(getattr(project, legacy_logo_field, None))
    if logo_url:
        return logo_url

    name = getattr(project, name_field, "")
    logo_url = _client_logo_url_by_name(name)
    if logo_url:
        return logo_url

    if include_company:
        return _company_logo_url_by_name(name)
    return ""


def project_list(request):
    settings = ProjectListPageSettings.objects.first() or ProjectListPageSettings()
    categories = ProjectCategory.objects.filter(is_active=True)
    projects = Project.objects.filter(is_active=True).select_related("category")
    category_slug = request.GET.get("category")
    query = request.GET.get("q")
    status = request.GET.get("status")
    year = request.GET.get("year")
    sort = request.GET.get("sort", "-year")
    # Render all active projects so the public page can filter instantly without reload.
    # Query parameters are still read and applied by the frontend on first load.
    if sort in ["year", "-year", "title", "-created_at", "sort_order"]:
        projects = projects.order_by(sort, "sort_order", "title")
    featured_project = Project.objects.filter(is_active=True, is_featured=True).first()
    if featured_project:
        projects = projects.exclude(id=featured_project.id)
    years = Project.objects.filter(is_active=True, year__isnull=False).values_list("year", flat=True).distinct().order_by("-year")
    return render(request, "projects/project_list.html", {
        "project_page_settings": settings,
        "categories": categories,
        "projects": projects,
        "featured_project": featured_project,
        "project_stats": ProjectListStat.objects.filter(is_active=True),
        "featured_clients": Client.objects.filter(is_active=True, is_featured=True).order_by("sort_order", "name")[:12],
        "active_category": category_slug,
        "query": query or "",
        "active_status": status or "",
        "active_year": year or "",
        "years": years,
        "sort": sort,
        "meta_title": "SESCCO Project Experience | Engineering & Contracting Portfolio",
        "meta_description": "Review SESCCO electrical, civil, architectural fitout and industrial project experience across Saudi Arabia.",
    })


def project_detail(request, slug):
    detail_settings = ProjectDetailPageSettings.objects.first() or ProjectDetailPageSettings()
    project = get_object_or_404(
        Project.objects
        .select_related("category", "client", "contractor")
        .prefetch_related("metrics", "gallery", "scope_items", "documents", "services"),
        slug=slug,
        is_active=True,
    )
    related_projects = Project.objects.filter(is_active=True, category=project.category).exclude(id=project.id)[:3]
    cover_name = project.cover_image.name if project.cover_image else None
    gallery_images = [
        image for image in project.gallery.all()
        if image.is_active and image.image and image.image.name != cover_name
    ]
    description_visual = gallery_images[-1] if gallery_images else None
    return render(request, "projects/project_detail.html", {
        "project": project,
        "detail_settings": detail_settings,
        "related_projects": related_projects,
        "gallery_images": gallery_images,
        "description_visual": description_visual,
        "project_client_logo_url": _stakeholder_logo_url(project, "client", "client_logo", "client_name"),
        "project_contractor_logo_url": _stakeholder_logo_url(project, "contractor", "contractor_logo", "contractor_name", include_company=True),
        "meta_title": project.seo_title or project.title,
        "meta_description": project.seo_description or project.short_description,
        "meta_image_url": project.cover_image.url if project.cover_image else "",
    })
