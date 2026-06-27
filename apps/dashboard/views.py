from collections import OrderedDict
from pathlib import Path

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.careers.forms import (
    ApplicationBulkStatusForm,
    ApplicationDashboardFilterForm,
    ApplicationReviewForm,
    InterviewInvitationForm,
    RejectionEmailForm,
)
from apps.careers.models import CareerDepartment, CareerPageSettings, JobApplication, JobApplicationDocument, JobOpening
from apps.clients.models import Certificate, Client, Partner, Testimonial
from apps.core.models import LocalizedContent
from apps.core.translation_registry import TRANSLATION_TARGETS
from apps.documents.models import DocumentRequest, DownloadDocument
from apps.inquiries.models import ContactInquiry
from apps.pages.models import Page
from apps.projects.models import Project
from apps.services.models import Service
from .models import ActivityLog



def _secure_application_file_response(file_obj):
    if not file_obj:
        raise Http404("Document not found.")
    try:
        handle = file_obj.open("rb")
    except Exception as exc:
        raise Http404("Document not available.") from exc
    filename = Path(file_obj.name).name or "career-document"
    return FileResponse(handle, as_attachment=True, filename=filename)


@staff_member_required
def career_application_field_download(request, pk, field_name):
    allowed_fields = {"cv", "supporting_document", "certificate_document"}
    if field_name not in allowed_fields:
        raise Http404("Document not found.")
    application = get_object_or_404(JobApplication, pk=pk)
    return _secure_application_file_response(getattr(application, field_name, None))


@staff_member_required
def career_application_document_download(request, pk, document_pk):
    document = get_object_or_404(JobApplicationDocument, pk=document_pk, application_id=pk)
    return _secure_application_file_response(document.file)

@staff_member_required
def dashboard_home(request):
    context = {
        "total_pages": Page.objects.count(),
        "total_services": Service.objects.count(),
        "total_projects": Project.objects.count(),
        "total_clients": Client.objects.count(),
        "total_partners": Partner.objects.count(),
        "total_certificates": Certificate.objects.count(),
        "total_documents": DownloadDocument.objects.count(),
        "total_document_requests": DocumentRequest.objects.filter(is_resolved=False).count(),
        "new_inquiries": ContactInquiry.objects.filter(status="new").count(),
        "spam_inquiries": ContactInquiry.objects.filter(is_spam_suspected=True).count(),
        "recent_inquiries": ContactInquiry.objects.all()[:6],
        "recent_document_requests": DocumentRequest.objects.all()[:6],
        "recent_updates": ActivityLog.objects.all()[:8],
        "total_testimonials": Testimonial.objects.count(),
        "career_jobs": JobOpening.objects.count(),
        "open_career_jobs": JobOpening.objects.filter(status="published", is_active=True).count(),
        "new_career_applications": JobApplication.objects.filter(status="new").count(),
        "shortlisted_career_applications": JobApplication.objects.filter(status="shortlisted").count(),
    }
    return render(request, "dashboard/dashboard.html", context)


@staff_member_required
def translation_dashboard(request):
    language = request.GET.get("language", "ar")
    rows = []
    for target in TRANSLATION_TARGETS:
        total = LocalizedContent.objects.filter(content_type=target.content_type, language_code=language).count()
        fields_count = len(target.fields)
        rows.append({
            "model_label": target.model_label,
            "content_type": target.content_type,
            "fields": ", ".join(target.fields),
            "translation_count": total,
            "registered_fields": fields_count,
        })
    return render(request, "dashboard/translation_dashboard.html", {
        "language": language,
        "rows": rows,
    })


def _apply_application_status(applications, status):
    updated = 0
    for application in applications:
        application.status = status
        application.save(update_fields=[
            "status",
            "status_updated_at",
            "reviewed_at",
            "shortlisted_at",
            "rejected_at",
            "hired_at",
            "updated_at",
        ])
        updated += 1
    return updated


def _filtered_applications(form):
    applications = JobApplication.objects.select_related("job", "job__department").prefetch_related("documents")
    if not form.is_valid():
        return applications.order_by("-created_at")

    q = form.cleaned_data.get("q")
    job = form.cleaned_data.get("job")
    department = form.cleaned_data.get("department")
    status = form.cleaned_data.get("status")
    date_from = form.cleaned_data.get("date_from")
    date_to = form.cleaned_data.get("date_to")
    sort = form.cleaned_data.get("sort") or "newest"

    if q:
        applications = applications.filter(
            Q(application_reference__icontains=q)
            | Q(full_name__icontains=q)
            | Q(email__icontains=q)
            | Q(alternate_email__icontains=q)
            | Q(phone__icontains=q)
            | Q(current_location__icontains=q)
            | Q(nationality__icontains=q)
            | Q(job__title__icontains=q)
            | Q(job__job_code__icontains=q)
        )
    if job:
        applications = applications.filter(job=job)
    if department:
        applications = applications.filter(job__department=department)
    if status:
        applications = applications.filter(status=status)
    if date_from:
        applications = applications.filter(created_at__date__gte=date_from)
    if date_to:
        applications = applications.filter(created_at__date__lte=date_to)

    ordering = {
        "oldest": ("created_at",),
        "status": ("status", "-created_at"),
        "job": ("job__title", "-created_at"),
        "interview": ("interview_date", "-created_at"),
        "newest": ("-created_at",),
    }.get(sort, ("-created_at",))
    return applications.order_by(*ordering)


@staff_member_required
def career_applications_dashboard(request):
    if request.method == "POST":
        selected_ids = request.POST.getlist("selected_applications")
        bulk_form = ApplicationBulkStatusForm(request.POST)
        if not selected_ids:
            messages.warning(request, "Select at least one applicant before applying a bulk action.")
            return redirect(request.get_full_path())
        if bulk_form.is_valid():
            status = bulk_form.cleaned_data["bulk_status"]
            selected = JobApplication.objects.filter(id__in=selected_ids)
            updated = _apply_application_status(selected, status)
            status_label = dict(JobApplication.STATUS_CHOICES).get(status, status)
            messages.success(request, f"{updated} applicant(s) moved to {status_label}.")
        else:
            messages.error(request, "Could not apply the selected bulk action. Please try again.")
        query_string = request.GET.urlencode()
        redirect_url = reverse("career_applications_dashboard")
        if query_string:
            redirect_url = f"{redirect_url}?{query_string}"
        return redirect(redirect_url)

    filter_form = ApplicationDashboardFilterForm(request.GET or None)
    bulk_form = ApplicationBulkStatusForm()
    applications = _filtered_applications(filter_form)

    paginator = Paginator(applications, 25)
    page_obj = paginator.get_page(request.GET.get("page"))

    grouped_applications = OrderedDict()
    for application in page_obj.object_list:
        grouped_applications.setdefault(application.job, []).append(application)

    status_counts = dict(JobApplication.objects.values("status").annotate(total=Count("id")).values_list("status", "total"))
    status_cards = []
    for status, label in JobApplication.STATUS_CHOICES:
        status_cards.append({"status": status, "label": label, "count": status_counts.get(status, 0)})

    today = timezone.localdate()
    job_summary = (
        JobOpening.objects.annotate(
            total_applications=Count("applications"),
            new_applications=Count("applications", filter=Q(applications__status="new")),
            shortlisted_applications=Count("applications", filter=Q(applications__status="shortlisted")),
            invited_applications=Count("applications", filter=Q(applications__status="interview_invited")),
        )
        .filter(total_applications__gt=0)
        .order_by("-total_applications", "title")[:10]
    )

    query_params = request.GET.copy()
    query_params.pop("page", None)

    context = {
        "filter_form": filter_form,
        "bulk_form": bulk_form,
        "page_obj": page_obj,
        "applications": page_obj.object_list,
        "grouped_applications": grouped_applications,
        "status_cards": status_cards,
        "total_applications": JobApplication.objects.count(),
        "filtered_total": applications.count(),
        "today_applications": JobApplication.objects.filter(created_at__date=today).count(),
        "open_jobs": JobOpening.objects.filter(status="published", is_active=True).count(),
        "departments_count": CareerDepartment.objects.count(),
        "job_summary": job_summary,
        "query_params": query_params.urlencode(),
    }
    return render(request, "dashboard/career_applications.html", context)


@staff_member_required
def career_application_detail(request, pk):
    application = get_object_or_404(
        JobApplication.objects.select_related("job", "job__department").prefetch_related("documents", "email_logs"),
        pk=pk,
    )
    career_settings = CareerPageSettings.objects.first() or CareerPageSettings()

    review_form = ApplicationReviewForm(instance=application)
    invitation_form = InterviewInvitationForm(instance=application, career_settings=career_settings)
    rejection_form = RejectionEmailForm(career_settings=career_settings)

    if request.method == "POST":
        action = request.POST.get("action", "save_review")
        if action == "quick_send_interview":
            try:
                application.send_interview_invitation(request=request, user=request.user)
                messages.success(request, f"Interview invitation sent to {application.full_name}.")
                return redirect("career_application_detail", pk=application.pk)
            except Exception as exc:
                messages.error(request, f"Interview invitation could not be sent: {exc}")
        elif action == "send_interview":
            invitation_form = InterviewInvitationForm(request.POST, instance=application, career_settings=career_settings)
            if invitation_form.is_valid():
                updated_application = invitation_form.save(commit=False)
                updated_application.save(update_fields=[
                    "interview_date",
                    "interview_mode",
                    "interview_location",
                    "interview_notes",
                    "updated_at",
                ])
                try:
                    updated_application.send_interview_invitation(
                        user=request.user,
                        subject_template=invitation_form.cleaned_data["email_subject"],
                        body_template=invitation_form.cleaned_data["email_body"],
                    )
                    messages.success(request, f"Interview invitation sent to {updated_application.full_name}.")
                    return redirect("career_application_detail", pk=application.pk)
                except Exception as exc:
                    messages.error(request, f"Interview invitation could not be sent: {exc}")
            else:
                messages.error(request, "Please complete the required interview invitation details.")
        elif action == "send_rejection":
            rejection_form = RejectionEmailForm(request.POST, career_settings=career_settings)
            if rejection_form.is_valid():
                try:
                    application.send_rejection_email(
                        user=request.user,
                        subject_template=rejection_form.cleaned_data["email_subject"],
                        body_template=rejection_form.cleaned_data["email_body"],
                        rejection_reason=rejection_form.cleaned_data.get("rejection_reason", ""),
                    )
                    messages.success(request, f"Rejection email sent to {application.full_name} and application marked as Rejected.")
                    return redirect("career_application_detail", pk=application.pk)
                except Exception as exc:
                    messages.error(request, f"Rejection email could not be sent: {exc}")
            else:
                messages.error(request, "Please check the rejection email fields.")
        else:
            review_form = ApplicationReviewForm(request.POST, instance=application)
            if review_form.is_valid():
                updated_application = review_form.save(commit=False)
                updated_application.save()
                messages.success(request, "Applicant review details updated.")
                return redirect("career_application_detail", pk=application.pk)
            messages.error(request, "Please check the review form fields.")

    documents = []
    for field_name, label in (("cv", "CV / Resume"), ("supporting_document", "Supporting Document"), ("certificate_document", "Certificate / License")):
        file_obj = getattr(application, field_name, None)
        if file_obj:
            documents.append({"label": label, "title": file_obj.name.split("/")[-1], "url": reverse("career_application_field_download", kwargs={"pk": application.pk, "field_name": field_name}), "source": "Applicant"})
    for document in application.documents.all():
        if document.file:
            documents.append({
                "label": document.get_document_type_display(),
                "title": document.title or document.file.name.split("/")[-1],
                "url": reverse("career_application_document_download", kwargs={"pk": application.pk, "document_pk": document.pk}),
                "source": "Applicant" if document.uploaded_by_applicant else "Admin",
                "notes": document.notes,
            })

    context = {
        "application": application,
        "form": review_form,
        "review_form": review_form,
        "invitation_form": invitation_form,
        "rejection_form": rejection_form,
        "documents": documents,
        "email_logs": application.email_logs.all()[:10],
        "status_cards": [{"status": status, "label": label} for status, label in JobApplication.STATUS_CHOICES],
    }
    return render(request, "dashboard/career_application_detail.html", context)

