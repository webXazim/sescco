from django.shortcuts import render
from apps.documents.models import DownloadDocument
from .models import (
    Accreditation, Certificate, Client, ClientCategory, ComplianceBlock, Partner,
    Standard, Testimonial, TrustMetric, TrustPageSettings
)


def clients_certifications(request):
    settings = TrustPageSettings.objects.first() or TrustPageSettings()
    clients = Client.objects.filter(is_active=True).select_related("category_ref")
    category_slug = request.GET.get("client_category")
    if category_slug:
        clients = clients.filter(category_ref__slug=category_slug)

    certificates = Certificate.objects.filter(is_active=True).select_related("category_ref")
    show_expired = request.GET.get("show_expired")
    if not show_expired:
        # Keep simple DB-compatible logic: expired status is shown in template/admin.
        pass

    return render(request, "clients/clients_certifications.html", {
        "trust_settings": settings,
        "trust_metrics": TrustMetric.objects.filter(is_active=True),
        "client_categories": ClientCategory.objects.filter(is_active=True),
        "active_client_category": category_slug or "",
        "clients": clients,
        # Contractors are kept for project detail records and admin entry, but are no longer shown as a public section on this page.
        "partners": Partner.objects.none(),
        "certificates": certificates,
        "accreditations": Accreditation.objects.filter(is_active=True),
        "standards": Standard.objects.filter(is_active=True),
        "compliance_blocks": ComplianceBlock.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_active=True, is_featured=True),
        "documents": DownloadDocument.objects.filter(is_active=True, is_public=True).select_related("category").order_by("-is_featured", "sort_order", "title")[:8],
        "meta_title": "SESCCO Certifications & Clients",
        "meta_description": "Review SESCCO certificates, compliance standards and client references.",
    })
