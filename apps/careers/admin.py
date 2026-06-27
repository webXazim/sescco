import re
from django import forms
from django.contrib import admin, messages
from django.utils import timezone
from django.urls import path, reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html, format_html_join, strip_tags

from .models import (
    CareerBenefit,
    CareerDepartment,
    CareerPageSettings,
    CareerProcessStep,
    CareerStat,
    CareerEmailVerification,
    JobApplication,
    JobApplicationDocument,
    JobApplicationEmailLog,
    JobOpening,
)


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(CareerPageSettings)
class CareerPageSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("SEO", {"fields": ("meta_title", "meta_description")} ),
        ("Hero", {"fields": ("eyebrow", "hero_title", "hero_subtitle", "hero_image")} ),
        ("Hero Buttons", {"fields": ("hero_primary_button_text", "hero_primary_button_url", "hero_secondary_button_text", "hero_secondary_button_url")} ),
        ("Open Roles Section", {"fields": ("intro_eyebrow", "intro_title", "intro_text", "empty_jobs_title", "empty_jobs_text")} ),
        ("Benefits Section", {"fields": ("show_benefits", "benefits_eyebrow", "benefits_title", "benefits_text")} ),
        ("Hiring Process", {"fields": ("show_process", "process_eyebrow", "process_title", "process_text")} ),
        ("Application Page", {"fields": ("form_help_title", "form_help_text", "application_guide_title", "application_guide_text", "applicant_profile_title", "applicant_profile_text", "document_upload_title", "document_upload_text", "duplicate_application_title", "duplicate_application_text", "privacy_notice")} ),
        ("Success Page", {"fields": ("success_eyebrow", "success_title", "success_text")} ),
        ("CTA", {"fields": ("show_cta", "cta_title", "cta_text", "cta_button_text", "cta_button_url", "recruitment_email")} ),
        ("HR Email Templates", {"fields": ("email_from_name", "email_verification_subject", "email_verification_body", "interview_email_subject", "interview_email_body", "rejection_email_subject", "rejection_email_body")} ),
        ("Visibility", {"fields": ("show_filters", "show_stats")} ),
    )


@admin.register(CareerStat)
class CareerStatAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "show_on_hero", "sort_order", "is_active")
    list_editable = ("show_on_hero", "sort_order", "is_active")
    search_fields = ("value", "label", "description")


@admin.register(CareerBenefit)
class CareerBenefitAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_text", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "description")


@admin.register(CareerProcessStep)
class CareerProcessStepAdmin(admin.ModelAdmin):
    list_display = ("step_number", "title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("step_number", "title", "description")


@admin.register(CareerDepartment)
class CareerDepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")



def _admin_plain_text(value):
    """Display legacy seeded HTML as clean editable text in Django admin."""
    text = str(value or "")
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</li\s*>", "\n", text, flags=re.I)
    text = strip_tags(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


class JobOpeningAdminForm(forms.ModelForm):
    class Meta:
        model = JobOpening
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Some older seed data stored job descriptions as <p>...</p> HTML.
        # Admin users should edit clean text, not visible HTML tags.
        if self.instance and self.instance.pk and self.instance.job_description:
            self.initial["job_description"] = _admin_plain_text(self.instance.job_description)
        self.fields["job_description"].widget.attrs.update({
            "rows": 7,
            "placeholder": "Write a clean paragraph-style job description. HTML tags are not required.",
        })
        for field_name in ("responsibilities", "requirements", "qualifications", "skills", "benefits"):
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.setdefault("rows", 6)

    def clean_job_description(self):
        return _admin_plain_text(self.cleaned_data.get("job_description"))


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    fields = ("application_reference", "full_name", "email", "phone", "status", "document_count", "created_at")
    readonly_fields = ("application_reference", "full_name", "email", "phone", "status", "document_count", "created_at")
    can_delete = False
    show_change_link = True


@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    form = JobOpeningAdminForm
    actions = ["publish_jobs", "close_jobs", "mark_on_hold", "mark_draft"]
    list_display = (
        "title",
        "job_code",
        "department",
        "location",
        "employment_type",
        "job_level",
        "status",
        "application_deadline",
        "applications_count",
        "applications_dashboard_link",
        "is_featured",
        "sort_order",
        "is_active",
    )
    list_editable = ("status", "is_featured", "sort_order", "is_active")
    list_filter = ("status", "department", "employment_type", "work_mode", "job_level", "is_featured", "is_active")
    search_fields = ("title", "job_code", "summary", "job_description", "location", "requirements", "skills")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"
    inlines = [JobApplicationInline]
    readonly_fields = ("created_at", "updated_at", "published_at", "closed_at", "applications_count", "public_job_link", "applications_dashboard_link")
    fieldsets = (
        ("Basic Job Information", {"fields": ("title", "slug", "job_code", "department", "summary", "public_job_link")} ),
        ("Job Details", {"fields": ("location", "employment_type", "work_mode", "job_level", "experience_level", "positions_available", "application_deadline")} ),
        ("Job Content", {"fields": ("job_description", "responsibilities", "requirements", "qualifications", "skills", "benefits")} ),
        ("Salary / Compensation", {"fields": ("show_salary", "salary_range", "salary_note")} ),
        ("Application Settings", {"fields": ("apply_button_text", "external_application_url", "contact_email")} ),
        ("Publishing", {"fields": ("status", "is_featured", "sort_order", "is_active", "published_at", "closed_at")} ),
        ("SEO", {"fields": ("seo_title", "seo_description")} ),
        ("System", {"fields": ("created_at", "updated_at", "applications_count", "applications_dashboard_link"), "classes": ("collapse",)} ),
    )

    def applications_count(self, obj):
        if not obj.pk:
            return 0
        return obj.applications.count()

    applications_count.short_description = "Applications"

    def applications_dashboard_link(self, obj):
        if not obj.pk:
            return "Save this job first to review applications."
        url = reverse("career_applications_dashboard") + f"?job={obj.pk}"
        return format_html('<a class="button" href="{}">Review applications</a>', url)

    applications_dashboard_link.short_description = "Applications Dashboard"

    def public_job_link(self, obj):
        if not obj.pk or not obj.slug:
            return "Save this job first to generate the public link."
        return format_html('<a class="button" href="/careers/{}/" target="_blank" rel="noopener">Open public job page</a>', obj.slug)

    public_job_link.short_description = "Public Page"

    def publish_jobs(self, request, queryset):
        updated = queryset.update(status="published", is_active=True, published_at=timezone.now())
        self.message_user(request, f"{updated} job(s) published and visible on the Careers page.", messages.SUCCESS)

    publish_jobs.short_description = "Publish selected jobs"

    def close_jobs(self, request, queryset):
        updated = queryset.update(status="closed", closed_at=timezone.now())
        self.message_user(request, f"{updated} job(s) closed.", messages.SUCCESS)

    close_jobs.short_description = "Close selected jobs"

    def mark_on_hold(self, request, queryset):
        updated = queryset.update(status="on_hold")
        self.message_user(request, f"{updated} job(s) marked as on hold.", messages.SUCCESS)

    mark_on_hold.short_description = "Mark selected jobs as on hold"

    def mark_draft(self, request, queryset):
        updated = queryset.update(status="draft")
        self.message_user(request, f"{updated} job(s) moved to draft.", messages.SUCCESS)

    mark_draft.short_description = "Move selected jobs to draft"


class ApplicationDocumentInline(admin.TabularInline):
    model = JobApplicationDocument
    extra = 0
    fields = ("document_type", "title", "file", "uploaded_by_applicant", "notes", "created_at")
    readonly_fields = ("created_at",)




class JobApplicationEmailLogInline(admin.TabularInline):
    model = JobApplicationEmailLog
    extra = 0
    can_delete = False
    fields = ("email_type", "recipient", "subject", "success", "sent_by", "created_at", "error_message")
    readonly_fields = fields
    max_num = 0

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    actions = ["mark_new", "mark_reviewed", "mark_shortlisted", "mark_rejected", "mark_hired", "send_interview_invitations", "send_rejection_emails"]
    list_display = (
        "application_reference",
        "full_name",
        "job",
        "email",
        "phone",
        "email_verified_display",
        "status_badge",
        "document_count_display",
        "dashboard_review_link",
        "one_click_invite",
        "interview_date",
        "invitation_sent_at",
        "rejection_sent_at",
        "created_at",
    )
    list_filter = ("status", "job", "job__department", "work_authorization", "source", "created_at", "invitation_sent_at", "rejection_sent_at")
    search_fields = (
        "application_reference",
        "full_name",
        "email",
        "alternate_email",
        "phone",
        "job__title",
        "job__job_code",
        "current_location",
        "nationality",
        "internal_notes",
    )
    readonly_fields = (
        "application_reference",
        "created_at",
        "updated_at",
        "status_updated_at",
        "reviewed_at",
        "shortlisted_at",
        "rejected_at",
        "hired_at",
        "invitation_sent_at",
        "rejection_sent_at",
        "submitted_ip",
        "user_agent",
        "email_verified",
        "email_verified_at",
        "document_links",
        "document_count_display",
        "dashboard_review_link",
        "quick_invite_action",
    )
    date_hierarchy = "created_at"
    inlines = [ApplicationDocumentInline, JobApplicationEmailLogInline]
    fieldsets = (
        ("Application Tracking", {"fields": ("application_reference", "job", "status", "status_updated_at", "created_at", "updated_at")} ),
        ("Applicant", {"fields": ("full_name", "email", "email_verified", "email_verified_at", "alternate_email", "phone", "current_location", "nationality", "work_authorization", "years_experience", "expected_salary", "available_from", "preferred_interview_time", "source")} ),
        ("Profile Links", {"fields": ("linkedin_url", "portfolio_url")} ),
        ("Applicant Message", {"fields": ("cover_letter", "consent")} ),
        ("Documents", {"fields": ("cv", "supporting_document", "certificate_document", "document_links", "document_count_display")} ),
        ("Review Dates", {"fields": ("reviewed_at", "shortlisted_at", "rejected_at", "hired_at"), "classes": ("collapse",)} ),
        ("Interview Invitation", {"fields": ("interview_date", "interview_mode", "interview_location", "interview_notes", "quick_invite_action", "invitation_sent_at", "rejection_sent_at")} ),
        ("Admin Notes", {"fields": ("internal_notes",)} ),
        ("Submission Metadata", {"fields": ("submitted_ip", "user_agent"), "classes": ("collapse",)} ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("job", "job__department").prefetch_related("documents")

    def status_badge(self, obj):
        palette = {
            "new": ("#e8f0ff", "#0758d8"),
            "reviewed": ("#eef6ff", "#0f5f99"),
            "shortlisted": ("#edf8f2", "#12803b"),
            "interview_invited": ("#fff7ed", "#b45309"),
            "rejected": ("#fef2f2", "#b91c1c"),
            "hired": ("#ecfdf5", "#047857"),
        }
        bg, color = palette.get(obj.status, ("#f3f4f6", "#374151"))
        return format_html('<span style="display:inline-flex;padding:4px 9px;border-radius:999px;background:{};color:{};font-weight:800;font-size:12px;">{}</span>', bg, color, obj.get_status_display())


    def email_verified_display(self, obj):
        if obj.email_verified:
            return format_html('<span style="display:inline-flex;padding:4px 9px;border-radius:999px;background:#ecfdf5;color:#047857;font-weight:800;font-size:12px;">Verified</span>')
        return format_html('<span style="display:inline-flex;padding:4px 9px;border-radius:999px;background:#fff7ed;color:#b45309;font-weight:800;font-size:12px;">Not verified</span>')

    email_verified_display.short_description = "Email"
    email_verified_display.admin_order_field = "email_verified"

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def document_count_display(self, obj):
        return obj.document_count if obj.pk else 0

    document_count_display.short_description = "Documents"

    def document_links(self, obj):
        if not obj.pk:
            return "Save the application first to see document links."
        links = []
        for field_name, label in (("cv", "CV"), ("supporting_document", "Supporting Document"), ("certificate_document", "Certificate")):
            file_obj = getattr(obj, field_name)
            if file_obj:
                url = reverse("career_application_field_download", kwargs={"pk": obj.pk, "field_name": field_name})
                links.append(format_html('<a class="button" href="{}" target="_blank" rel="noopener">Secure Download {}</a>', url, label))
        for document in obj.documents.all():
            if document.file:
                label = document.title or document.get_document_type_display()
                url = reverse("career_application_document_download", kwargs={"pk": obj.pk, "document_pk": document.pk})
                links.append(format_html('<a class="button" href="{}" target="_blank" rel="noopener">Secure Download {}</a>', url, label))
        return format_html_join(format_html("<br><br>"), "{}", ((link,) for link in links)) if links else "No documents uploaded."

    document_links.short_description = "Applicant Documents"

    def dashboard_review_link(self, obj):
        if not obj.pk:
            return "Save first"
        url = reverse("career_application_detail", kwargs={"pk": obj.pk})
        return format_html('<a class="button" href="{}">Review dashboard</a>', url)

    dashboard_review_link.short_description = "Review"

    def get_urls(self):
        custom_urls = [
            path(
                "<int:application_id>/send-interview-invite/",
                self.admin_site.admin_view(self.send_interview_invite_now_view),
                name="careers_jobapplication_send_interview_invite",
            ),
        ]
        return custom_urls + super().get_urls()

    def send_interview_invite_now_view(self, request, application_id):
        application = get_object_or_404(JobApplication, pk=application_id)
        if not self.has_change_permission(request, application):
            raise PermissionDenied
        try:
            application.send_interview_invitation(request=request, user=request.user)
            self.message_user(request, f"Interview invitation sent to {application.full_name}.", messages.SUCCESS)
        except Exception as exc:
            self.message_user(request, f"Interview invitation could not be sent: {exc}", messages.ERROR)
        return redirect("admin:careers_jobapplication_change", application.pk)

    def one_click_invite(self, obj):
        if not obj.pk:
            return "Save first"
        if obj.invitation_sent_at:
            return format_html('<span style="color:#047857;font-weight:800;">Sent</span>')
        if not obj.has_invitation_details:
            return format_html('<span style="color:#b45309;font-weight:800;">Add interview date/link</span>')
        url = reverse("admin:careers_jobapplication_send_interview_invite", args=[obj.pk])
        return format_html('<a class="button" href="{}">Send Invite</a>', url)

    one_click_invite.short_description = "Quick Invite"

    def quick_invite_action(self, obj):
        if not obj.pk:
            return "Save this application first."
        if obj.invitation_sent_at:
            return format_html('<span style="display:inline-flex;padding:6px 10px;border-radius:999px;background:#ecfdf5;color:#047857;font-weight:800;">Invitation already sent on {}</span>', obj.invitation_sent_at.strftime("%b %d, %Y %H:%M"))
        if not obj.has_invitation_details:
            return format_html('<span style="display:inline-flex;padding:6px 10px;border-radius:999px;background:#fff7ed;color:#b45309;font-weight:800;">Add interview date and location/link, save, then send with one click.</span>')
        url = reverse("admin:careers_jobapplication_send_interview_invite", args=[obj.pk])
        return format_html('<a class="button" href="{}" style="background:#0758d8;color:#fff;border-color:#0758d8;">Send interview invite now</a>', url)

    quick_invite_action.short_description = "One-click Interview Invite"

    def _set_status(self, request, queryset, status):
        updated = 0
        for application in queryset:
            application.status = status
            application.save(update_fields=["status", "status_updated_at", "reviewed_at", "shortlisted_at", "rejected_at", "hired_at", "updated_at"])
            updated += 1
        self.message_user(request, f"{updated} application(s) marked as {dict(JobApplication.STATUS_CHOICES)[status]}.", messages.SUCCESS)

    def mark_new(self, request, queryset):
        self._set_status(request, queryset, "new")

    mark_new.short_description = "Mark selected applications as New"

    def mark_reviewed(self, request, queryset):
        self._set_status(request, queryset, "reviewed")

    mark_reviewed.short_description = "Mark selected applications as Reviewed"

    def mark_shortlisted(self, request, queryset):
        self._set_status(request, queryset, "shortlisted")

    mark_shortlisted.short_description = "Shortlist selected applications"

    def mark_rejected(self, request, queryset):
        self._set_status(request, queryset, "rejected")

    mark_rejected.short_description = "Reject selected applications"

    def mark_hired(self, request, queryset):
        self._set_status(request, queryset, "hired")

    mark_hired.short_description = "Mark selected applications as Hired"

    def send_interview_invitations(self, request, queryset):
        sent = 0
        skipped = 0
        errors = []
        for application in queryset:
            if not application.has_invitation_details:
                skipped += 1
                continue
            try:
                application.send_interview_invitation(request=request, user=request.user)
                sent += 1
            except Exception as exc:  # keep admin action safe
                errors.append(f"{application.full_name}: {exc}")
        if sent:
            self.message_user(request, f"Interview invitation sent to {sent} applicant(s).", messages.SUCCESS)
        if skipped:
            self.message_user(request, f"{skipped} applicant(s) skipped because interview date or location/link is missing.", messages.WARNING)
        if errors:
            self.message_user(request, "Some invitations failed: " + " | ".join(errors), messages.ERROR)

    send_interview_invitations.short_description = "Send interview invitation email to selected applicants"


    def send_rejection_emails(self, request, queryset):
        sent = 0
        errors = []
        for application in queryset:
            try:
                application.send_rejection_email(request=request, user=request.user)
                sent += 1
            except Exception as exc:  # keep admin action safe
                errors.append(f"{application.full_name}: {exc}")
        if sent:
            self.message_user(request, f"Rejection email sent to {sent} applicant(s).", messages.SUCCESS)
        if errors:
            self.message_user(request, "Some rejection emails failed: " + " | ".join(errors), messages.ERROR)

    send_rejection_emails.short_description = "Send rejection email to selected applicants"



@admin.register(CareerEmailVerification)
class CareerEmailVerificationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "email", "job", "verified_at", "used_at", "expires_at", "attempts", "sent_ip")
    list_filter = ("verified_at", "used_at", "expires_at", "created_at")
    search_fields = ("email", "job__title", "job__job_code", "sent_ip")
    readonly_fields = ("job", "email", "code_hash", "expires_at", "verified_at", "used_at", "send_count", "attempts", "sent_ip", "user_agent", "created_at", "updated_at")

    def has_add_permission(self, request):
        return False


@admin.register(JobApplicationDocument)
class JobApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "application", "document_type", "uploaded_by_applicant", "secure_download_link", "created_at")
    list_filter = ("document_type", "uploaded_by_applicant", "created_at")
    search_fields = ("title", "application__application_reference", "application__full_name", "application__email")
    readonly_fields = ("created_at", "updated_at", "secure_download_link")

    def secure_download_link(self, obj):
        if not obj.pk or not obj.file:
            return "Save first"
        url = reverse("career_application_document_download", kwargs={"pk": obj.application_id, "document_pk": obj.pk})
        return format_html('<a class="button" href="{}" target="_blank" rel="noopener">Secure Download</a>', url)

    secure_download_link.short_description = "Download"

@admin.register(JobApplicationEmailLog)
class JobApplicationEmailLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "application", "email_type", "recipient", "subject", "success", "sent_by")
    list_filter = ("email_type", "success", "created_at")
    search_fields = ("application__application_reference", "application__full_name", "recipient", "subject", "body", "error_message")
    readonly_fields = ("created_at", "updated_at", "application", "email_type", "recipient", "subject", "body", "sent_by", "success", "error_message", "interview_date", "interview_mode", "interview_location")

    def has_add_permission(self, request):
        return False

