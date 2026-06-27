from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from apps.projects.models import Project
from .models import Service, ServiceCategory, ServiceDetailPageSettings, ServiceListFAQ, ServiceListPageSettings, ServiceListProcessStep


def service_list(request):
    settings = ServiceListPageSettings.objects.first() or ServiceListPageSettings()
    categories = ServiceCategory.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True).select_related("category")
    category_slug = request.GET.get("category", "").strip()
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "default").strip() or "default"
    # Render all active services and let the frontend filter in real time.
    # Keeping all cards in the DOM makes search/category changes instant without a page reload.

    if sort == "title":
        services = services.order_by("title", "sort_order", "id")
    elif sort == "featured":
        services = services.order_by("-is_featured", "sort_order", "id")
    elif sort == "newest":
        services = services.order_by("-created_at", "sort_order", "id")
    else:
        services = services.order_by("sort_order", "id")

    featured_service = Service.objects.filter(is_active=True, is_featured=True).first()
    return render(request, "services/service_list.html", {
        "service_page_settings": settings,
        "categories": categories,
        "services": services,
        "featured_service": featured_service,
        "process_steps": ServiceListProcessStep.objects.filter(is_active=True),
        "service_list_faqs": ServiceListFAQ.objects.filter(is_active=True),
        "active_category": category_slug,
        "query": query or "",
        "sort": sort,
        "meta_title": "SESCCO Services | Electrical, Civil, Fitout & Contract Support",
        "meta_description": "Explore SESCCO engineering services including electrical works, civil works, architectural fitout, HVAC, fire systems, plumbing and contract support.",
    })


def service_detail(request, slug):
    detail_settings = ServiceDetailPageSettings.objects.first() or ServiceDetailPageSettings()
    service = get_object_or_404(
        Service.objects
        .select_related("category")
        .prefetch_related("key_points", "deliverables", "features", "process_steps", "faqs"),
        slug=slug,
        is_active=True,
    )
    related_projects = Project.objects.filter(is_active=True, services=service)[:4]
    return render(request, "services/service_detail.html", {
        "service": service,
        "detail_settings": detail_settings,
        "related_projects": related_projects,
        "meta_title": service.seo_title or service.title,
        "meta_description": service.seo_description or service.short_description,
        "meta_image_url": service.cover_image.url if service.cover_image else "",
    })
