from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import DocumentRequestForm
from .models import DocumentCategory, DocumentPageCTA, DocumentRequest, DownloadDocument, DownloadLog, DownloadsPageSettings


def downloads(request):
    # The public Downloads landing page has been replaced by the Careers page.
    # Old /downloads/ links now land on the new career section instead of showing an extra page.
    return redirect("career_list")


def legacy_downloads_archive(request):
    settings = DownloadsPageSettings.objects.first() or DownloadsPageSettings()
    cta = DocumentPageCTA.objects.filter(is_active=True).first()
    categories = DocumentCategory.objects.filter(is_active=True)
    documents = DownloadDocument.objects.filter(is_active=True, is_public=True).select_related("category")
    category_slug = request.GET.get("category")
    query = request.GET.get("q")
    file_type = request.GET.get("file_type")
    sort = request.GET.get("sort", "-updated_at")
    if category_slug:
        documents = documents.filter(category__slug=category_slug)
    if query:
        documents = documents.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(version__icontains=query))
    if file_type:
        documents = documents.filter(file_type__iexact=file_type)
    if sort in ["title", "-updated_at", "download_count", "-download_count", "sort_order"]:
        documents = documents.order_by(sort)
    featured_document = DownloadDocument.objects.filter(is_active=True, is_featured=True, is_public=True).first()
    file_types = DownloadDocument.objects.filter(is_active=True, is_public=True).values_list("file_type", flat=True).distinct()
    return render(request, "documents/downloads.html", {
        "download_settings": settings,
        "document_cta": cta,
        "categories": categories,
        "documents": documents,
        "featured_document": featured_document,
        "active_category": category_slug,
        "query": query or "",
        "file_types": file_types,
        "active_file_type": file_type or "",
        "sort": sort,
        "meta_title": "SESCCO Downloads & Company Documents",
        "meta_description": "Download SESCCO company profile, capability sheets, vendor references and quality, safety and environmental commitment documents.",
    })


def download_file(request, slug):
    document = get_object_or_404(DownloadDocument, slug=slug, is_active=True, is_public=True)
    if document.access_level in ["request", "private"] or document.requires_request:
        messages.info(request, "This document requires a request before download.")
        return redirect("document_request")
    if not document.file:
        raise Http404("File not found")
    document.download_count += 1
    document.save(update_fields=["download_count"])
    DownloadLog.objects.create(document=document, ip_address=request.META.get("REMOTE_ADDR"), user_agent=request.META.get("HTTP_USER_AGENT", ""))
    return FileResponse(document.file.open("rb"), as_attachment=True)


def document_request(request):
    if request.method == "POST":
        form = DocumentRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your document request has been received. Our team will contact you soon.")
            return redirect("document_request")
    else:
        form = DocumentRequestForm(initial={"requested_document": request.GET.get("document", "")})
    return render(request, "documents/document_request.html", {"form": form, "meta_title": "Request SESCCO Document", "meta_description": "Request protected SESCCO company documents and project capability information."})
