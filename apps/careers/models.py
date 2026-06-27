from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.template import Context, Template
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import constant_time_compare, get_random_string, salted_hmac
from django.utils.text import get_valid_filename, slugify
from pathlib import Path
from uuid import uuid4

from apps.core.models import OrderedActiveModel, TimeStampedModel
from .validators import validate_career_cv_file, validate_career_document_file


def unique_slug_for(instance, value):
    """Generate a stable unique slug for admin-created CMS records."""
    base_slug = slugify(value) or "item"
    slug = base_slug
    model = instance.__class__
    counter = 2
    queryset = model.objects.filter(slug=slug)
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)
    while queryset.exists():
        slug = f"{base_slug}-{counter}"
        queryset = model.objects.filter(slug=slug)
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)
        counter += 1
    return slug


def _safe_private_document_name(filename):
    extension = Path(filename or "").suffix.lower()
    stem = get_valid_filename(Path(filename or "document").stem)[:48] or "document"
    return f"{stem}-{uuid4().hex[:12]}{extension}"


def application_file_path(instance, filename):
    """Store applicant files in a private career area with randomized names."""
    reference = getattr(instance, "application_reference", "") or "pending"
    return f"careers/private/applications/{reference}/{_safe_private_document_name(filename)}"


def application_extra_document_path(instance, filename):
    reference = getattr(instance.application, "application_reference", "") or "pending"
    return f"careers/private/applications/{reference}/documents/{_safe_private_document_name(filename)}"



DEFAULT_EMAIL_VERIFICATION_SUBJECT = "Verify your SESCCO career application email"
DEFAULT_EMAIL_VERIFICATION_BODY = """Dear applicant,

Use this verification code to continue your SESCCO job application:

{{ code }}

Position: {{ job.title }}
This code will expire in {{ expiry_minutes }} minutes.

If you did not request this code, please ignore this email.

Regards,
SESCCO HR Team
"""

DEFAULT_INTERVIEW_EMAIL_SUBJECT = "Interview Invitation — {{ job.title }}"
DEFAULT_INTERVIEW_EMAIL_BODY = """Dear {{ application.full_name }},

Thank you for applying for the {{ job.title }} position at SESCCO.

You have been shortlisted for an interview.

Application reference: {{ application.application_reference }}

Interview details:
Position: {{ job.title }}
Date and time: {{ application.interview_date|date:"l, F d, Y - h:i A" }}
Mode: {{ application.get_interview_mode_display }}
Location / meeting link: {{ application.interview_location }}
{% if application.interview_notes %}
Additional notes:
{{ application.interview_notes }}
{% endif %}
Please bring or keep ready your CV, identification and relevant certificates.

Regards,
SESCCO HR Team
"""

DEFAULT_REJECTION_EMAIL_SUBJECT = "Application Update — {{ job.title }}"
DEFAULT_REJECTION_EMAIL_BODY = """Dear {{ application.full_name }},

Thank you for applying for the {{ job.title }} position at SESCCO.

After carefully reviewing your application, we are unable to move forward with your profile for this role at this time.

Application reference: {{ application.application_reference }}

{% if rejection_reason %}Note from HR:
{{ rejection_reason }}
{% endif %}
We appreciate your interest in SESCCO and encourage you to apply again when a suitable opportunity is available.

Regards,
SESCCO HR Team
"""


def render_email_template(template_string, context):
    """Render admin-editable career email templates with normal Django variables."""
    return Template(template_string or "").render(Context(context)).strip()



def get_client_ip_from_request(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR") if request else ""
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR") if request else None

def career_from_email():
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None) or getattr(settings, "SERVER_EMAIL", None) or "no-reply@sescco.com"
    try:
        page_settings = CareerPageSettings.objects.first()
        if page_settings and page_settings.email_from_name:
            return f"{page_settings.email_from_name} <{from_email}>"
    except Exception:
        pass
    return from_email


class CareerPageSettings(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default="Careers")
    hero_title = models.CharField(max_length=255, default="Build Your Career with SESCCO")
    hero_subtitle = models.TextField(
        blank=True,
        default="Explore open positions, apply online and join a team committed to safe, reliable engineering execution.",
    )
    hero_image = models.ImageField(upload_to="careers/page/", blank=True, null=True)
    hero_primary_button_text = models.CharField(max_length=120, default="View Open Jobs")
    hero_primary_button_url = models.CharField(max_length=255, default="#open-roles")
    hero_secondary_button_text = models.CharField(max_length=120, default="Contact HR")
    hero_secondary_button_url = models.CharField(max_length=255, default="/contact/")

    meta_title = models.CharField(max_length=255, blank=True, default="Careers | SESCCO")
    meta_description = models.CharField(
        max_length=320,
        blank=True,
        default="Explore career opportunities at SESCCO and apply online with your CV and supporting documents.",
    )

    intro_eyebrow = models.CharField(max_length=120, default="Open Opportunities")
    intro_title = models.CharField(max_length=255, default="Find the right role for your next step")
    intro_text = models.TextField(
        blank=True,
        default="We review every application carefully and invite shortlisted candidates for interview through official email.",
    )
    empty_jobs_title = models.CharField(max_length=180, default="No open jobs found")
    empty_jobs_text = models.TextField(blank=True, default="Try another search or check again later for new opportunities.")

    benefits_eyebrow = models.CharField(max_length=120, default="Why Work With Us")
    benefits_title = models.CharField(max_length=255, default="A practical environment for serious professionals")
    benefits_text = models.TextField(
        blank=True,
        default="SESCCO career opportunities are built around project readiness, safe execution, technical growth and reliable teamwork.",
    )

    process_eyebrow = models.CharField(max_length=120, default="Hiring Process")
    process_title = models.CharField(max_length=255, default="Simple hiring process")
    process_text = models.TextField(blank=True, default="Apply, get reviewed, attend the interview and join the project team.")

    form_help_title = models.CharField(max_length=180, default="Before submitting")
    form_help_text = models.TextField(
        blank=True,
        default="Prepare a clear CV and attach documents that support the role. Make sure your email and phone number are correct.",
    )
    application_guide_title = models.CharField(max_length=180, default="Application checklist")
    application_guide_text = models.TextField(
        blank=True,
        default="Use PDF, DOC or DOCX files only. Shortlisted applicants will receive interview details by email.",
    )
    applicant_profile_title = models.CharField(max_length=180, default="Applicant profile")
    applicant_profile_text = models.TextField(
        blank=True,
        default="Add your location, work authorization, experience and useful profile links so HR can review the application faster.",
    )
    document_upload_title = models.CharField(max_length=180, default="Application documents")
    document_upload_text = models.TextField(
        blank=True,
        default="Upload your CV and any supporting certificates, licenses or project documents as PDF, DOC or DOCX files. Multiple additional documents are supported.",
    )
    duplicate_application_title = models.CharField(max_length=180, default="Application already submitted")
    duplicate_application_text = models.TextField(
        blank=True,
        default="This email has already been used to apply for this job. Please contact HR if you need to update your application.",
    )
    privacy_notice = models.TextField(
        blank=True,
        default="Your information will only be used for recruitment review and official communication about this application.",
    )
    success_eyebrow = models.CharField(max_length=120, default="Application Submitted")
    success_title = models.CharField(max_length=220, default="Thank you for applying.")
    success_text = models.TextField(
        blank=True,
        default="Your application has been received. Our HR team will review your CV and documents. Shortlisted applicants will receive an interview invitation by email.",
    )

    show_filters = models.BooleanField(default=True)
    show_stats = models.BooleanField(default=True)
    show_benefits = models.BooleanField(default=True)
    show_process = models.BooleanField(default=True)
    show_cta = models.BooleanField(default=True)

    cta_title = models.CharField(max_length=255, default="Didn’t find the exact role?")
    cta_text = models.TextField(blank=True, default="Check this page again soon or contact our HR team for future opportunities.")
    cta_button_text = models.CharField(max_length=120, default="Contact HR")
    cta_button_url = models.CharField(max_length=255, default="/contact/")
    recruitment_email = models.EmailField(blank=True, default="hr@sescco.com")
    email_from_name = models.CharField(max_length=140, blank=True, default="SESCCO HR Team")
    email_verification_subject = models.CharField(max_length=255, default=DEFAULT_EMAIL_VERIFICATION_SUBJECT)
    email_verification_body = models.TextField(default=DEFAULT_EMAIL_VERIFICATION_BODY)
    interview_email_subject = models.CharField(max_length=255, default=DEFAULT_INTERVIEW_EMAIL_SUBJECT)
    interview_email_body = models.TextField(default=DEFAULT_INTERVIEW_EMAIL_BODY)
    rejection_email_subject = models.CharField(max_length=255, default=DEFAULT_REJECTION_EMAIL_SUBJECT)
    rejection_email_body = models.TextField(default=DEFAULT_REJECTION_EMAIL_BODY)

    class Meta:
        verbose_name = "Career Page Settings"
        verbose_name_plural = "Career Page Settings"

    def __str__(self):
        return "Career Page Settings"


class CareerStat(OrderedActiveModel, TimeStampedModel):
    value = models.CharField(max_length=80)
    label = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=20, blank=True, default="")
    show_on_hero = models.BooleanField(default=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Career Stat"
        verbose_name_plural = "Career Stats"

    def __str__(self):
        return f"{self.value} {self.label}"


class CareerBenefit(OrderedActiveModel, TimeStampedModel):
    icon_text = models.CharField(max_length=20, blank=True, default="✓")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Career Benefit"
        verbose_name_plural = "Career Benefits"

    def __str__(self):
        return self.title


class CareerProcessStep(OrderedActiveModel, TimeStampedModel):
    step_number = models.CharField(max_length=12, blank=True, default="")
    title = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=20, blank=True, default="")

    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Career Process Step"
        verbose_name_plural = "Career Process Steps"

    def __str__(self):
        return self.title


class CareerDepartment(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Career Department"
        verbose_name_plural = "Career Departments"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_for(self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class JobOpening(OrderedActiveModel, TimeStampedModel):
    EMPLOYMENT_TYPES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("temporary", "Temporary"),
        ("internship", "Internship"),
    ]
    WORK_MODES = [
        ("site", "Site Based"),
        ("office", "Office Based"),
        ("hybrid", "Hybrid"),
        ("remote", "Remote"),
    ]
    JOB_LEVELS = [
        ("entry", "Entry Level"),
        ("junior", "Junior"),
        ("mid", "Mid Level"),
        ("senior", "Senior"),
        ("lead", "Lead / Supervisor"),
        ("manager", "Manager"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("on_hold", "On Hold"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    job_code = models.CharField(max_length=40, blank=True, default="", help_text="Optional internal reference, for example SES-ENG-001.")
    department = models.ForeignKey(CareerDepartment, on_delete=models.SET_NULL, related_name="jobs", blank=True, null=True)
    location = models.CharField(max_length=160, default="Dammam, Saudi Arabia")
    employment_type = models.CharField(max_length=30, choices=EMPLOYMENT_TYPES, default="full_time")
    work_mode = models.CharField(max_length=30, choices=WORK_MODES, default="site")
    job_level = models.CharField(max_length=30, choices=JOB_LEVELS, default="mid")
    experience_level = models.CharField(max_length=120, blank=True, default="Experienced")
    positions_available = models.PositiveIntegerField(default=1)
    application_deadline = models.DateField(blank=True, null=True)

    summary = models.TextField(help_text="Short card summary shown on the career listing page.")
    job_description = models.TextField(blank=True, default="", help_text="Full description shown on the job detail page.")
    responsibilities = models.TextField(blank=True, help_text="Use one line per responsibility.")
    requirements = models.TextField(blank=True, help_text="Use one line per requirement.")
    qualifications = models.TextField(blank=True, default="", help_text="Use one line per qualification, certificate or education requirement.")
    skills = models.TextField(blank=True, default="", help_text="Use one line per preferred skill.")
    benefits = models.TextField(blank=True, help_text="Use one line per benefit or note.")

    salary_range = models.CharField(max_length=120, blank=True, default="", help_text="Optional salary range, for example SAR 5,000 - 7,000.")
    salary_note = models.CharField(max_length=180, blank=True, default="", help_text="Optional note, for example Depends on experience.")
    show_salary = models.BooleanField(default=False, help_text="Turn on only when salary information should be public.")

    apply_button_text = models.CharField(max_length=120, default="Apply Now")
    external_application_url = models.URLField(blank=True, default="", help_text="Optional external apply link. Leave blank to use the built-in application form.")
    contact_email = models.EmailField(blank=True, help_text="Optional HR email for this role. Defaults to DEFAULT_FROM_EMAIL.")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="published")
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    closed_at = models.DateTimeField(blank=True, null=True)

    seo_title = models.CharField(max_length=255, blank=True, default="")
    seo_description = models.CharField(max_length=320, blank=True, default="")

    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Job Opening"
        verbose_name_plural = "Job Openings"
        indexes = [
            models.Index(fields=["status", "is_active", "application_deadline"]),
            models.Index(fields=["is_featured", "sort_order"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_for(self, self.title)
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        if self.status == "closed" and not self.closed_at:
            self.closed_at = timezone.now()
        if not self.seo_title:
            self.seo_title = f"{self.title} | SESCCO Careers"
        if not self.seo_description:
            self.seo_description = (self.summary or "")[:300]
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        if self.status != "published" or not self.is_active:
            return False
        if self.application_deadline and self.application_deadline < timezone.localdate():
            return False
        return True

    @property
    def display_salary(self):
        if not self.show_salary or not self.salary_range:
            return ""
        if self.salary_note:
            return f"{self.salary_range} — {self.salary_note}"
        return self.salary_range

    def lines(self, field_name):
        value = getattr(self, field_name, "") or ""
        return [line.strip() for line in value.splitlines() if line.strip()]

    @property
    def responsibility_list(self):
        return self.lines("responsibilities")

    @property
    def requirement_list(self):
        return self.lines("requirements")

    @property
    def qualification_list(self):
        return self.lines("qualifications")

    @property
    def skill_list(self):
        return self.lines("skills")

    @property
    def benefit_list(self):
        return self.lines("benefits")

    def __str__(self):
        return self.title


class JobApplication(TimeStampedModel):
    STATUS_CHOICES = [
        ("new", "New"),
        ("reviewed", "Reviewed"),
        ("shortlisted", "Shortlisted"),
        ("interview_invited", "Interview Invited"),
        ("rejected", "Rejected"),
        ("hired", "Hired"),
    ]
    INTERVIEW_MODES = [
        ("in_person", "In Person"),
        ("online", "Online"),
        ("phone", "Phone Call"),
    ]
    WORK_AUTHORIZATION_CHOICES = [
        ("", "Not specified"),
        ("saudi_national", "Saudi National"),
        ("transferable_iqama", "Transferable Iqama"),
        ("company_sponsorship", "Requires Company Sponsorship"),
        ("visit_or_temporary", "Visit / Temporary Visa"),
        ("other", "Other"),
    ]
    SOURCE_CHOICES = [
        ("", "Not specified"),
        ("website", "Company Website"),
        ("linkedin", "LinkedIn"),
        ("referral", "Employee Referral"),
        ("job_board", "Job Board"),
        ("walk_in", "Walk-in"),
        ("other", "Other"),
    ]

    job = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="applications")
    application_reference = models.CharField(max_length=40, unique=True, blank=True, editable=False, db_index=True)
    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    alternate_email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=60)
    current_location = models.CharField(max_length=160, blank=True)
    nationality = models.CharField(max_length=120, blank=True)
    work_authorization = models.CharField(max_length=40, choices=WORK_AUTHORIZATION_CHOICES, blank=True, default="")
    years_experience = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    expected_salary = models.CharField(max_length=120, blank=True)
    available_from = models.CharField(max_length=120, blank=True)
    preferred_interview_time = models.CharField(max_length=160, blank=True, default="")
    linkedin_url = models.URLField(blank=True, default="")
    portfolio_url = models.URLField(blank=True, default="")
    source = models.CharField(max_length=40, choices=SOURCE_CHOICES, blank=True, default="website")
    cover_letter = models.TextField(blank=True)
    cv = models.FileField(upload_to=application_file_path, validators=[validate_career_cv_file], help_text="Required CV / resume file. PDF, DOC or DOCX only.")
    supporting_document = models.FileField(upload_to=application_file_path, validators=[validate_career_document_file], blank=True, null=True, help_text="Optional PDF, DOC or DOCX document.")
    certificate_document = models.FileField(upload_to=application_file_path, validators=[validate_career_document_file], blank=True, null=True, help_text="Optional PDF, DOC or DOCX certificate/license document.")
    consent = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    status_updated_at = models.DateTimeField(blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    shortlisted_at = models.DateTimeField(blank=True, null=True)
    rejected_at = models.DateTimeField(blank=True, null=True)
    hired_at = models.DateTimeField(blank=True, null=True)
    internal_notes = models.TextField(blank=True)
    submitted_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")

    interview_date = models.DateTimeField(blank=True, null=True)
    interview_mode = models.CharField(max_length=30, choices=INTERVIEW_MODES, default="in_person")
    interview_location = models.CharField(max_length=255, blank=True, help_text="Office address, project site, phone number or meeting link.")
    interview_notes = models.TextField(blank=True, help_text="Extra instructions for the applicant.")
    invitation_sent_at = models.DateTimeField(blank=True, null=True)
    rejection_sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        indexes = [
            models.Index(fields=["job", "email"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        reference = self.application_reference or "Pending"
        return f"{reference} — {self.full_name} — {self.job.title}"

    @staticmethod
    def build_reference():
        stamp = timezone.now().strftime("%Y%m")
        return f"SES-{stamp}-{timezone.now().strftime('%d%H%M%S%f')[-8:]}"

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = type(self).objects.filter(pk=self.pk).values_list("status", flat=True).first()
        if not self.application_reference:
            reference = self.build_reference()
            while type(self).objects.filter(application_reference=reference).exists():
                reference = self.build_reference()
            self.application_reference = reference
        if self.email:
            self.email = self.email.strip().lower()
        if self.alternate_email:
            self.alternate_email = self.alternate_email.strip().lower()

        now = timezone.now()
        if not self.status_updated_at or (previous_status and previous_status != self.status):
            self.status_updated_at = now
        if self.status == "reviewed" and not self.reviewed_at:
            self.reviewed_at = now
        if self.status == "shortlisted" and not self.shortlisted_at:
            self.shortlisted_at = now
        if self.status == "rejected" and not self.rejected_at:
            self.rejected_at = now
        if self.status == "hired" and not self.hired_at:
            self.hired_at = now
        super().save(*args, **kwargs)

    @property
    def has_invitation_details(self):
        return bool(self.interview_date and self.interview_location)

    @property
    def document_count(self):
        count = 1 if self.cv else 0
        count += 1 if self.supporting_document else 0
        count += 1 if self.certificate_document else 0
        if self.pk:
            count += self.documents.count()
        return count

    def email_context(self, **extra):
        company = None
        try:
            from apps.core.models import CompanyProfile

            company = CompanyProfile.objects.first()
        except Exception:
            company = None
        context = {
            "application": self,
            "job": self.job,
            "company": company,
            "rejection_reason": extra.get("rejection_reason", ""),
        }
        context.update(extra)
        return context

    def _log_email(self, email_type, subject, body, recipient, sent_by=None, success=True, error_message=""):
        return JobApplicationEmailLog.objects.create(
            application=self,
            email_type=email_type,
            recipient=recipient,
            subject=subject,
            body=body,
            sent_by=sent_by if getattr(sent_by, "is_authenticated", False) else None,
            success=success,
            error_message=str(error_message)[:2000],
            interview_date=self.interview_date,
            interview_mode=self.interview_mode,
            interview_location=self.interview_location,
        )

    def send_career_email(self, email_type, subject_template, body_template, sent_by=None, context_extra=None):
        context = self.email_context(**(context_extra or {}))
        subject = render_email_template(subject_template, context).replace("\n", " ").strip()
        body = render_email_template(body_template, context)
        if not subject:
            subject = "SESCCO Career Update"
        if not body:
            raise ValueError("Email body cannot be empty.")
        recipient = self.email
        try:
            send_mail(subject, body, career_from_email(), [recipient], fail_silently=False)
        except Exception as exc:
            self._log_email(email_type, subject, body, recipient, sent_by=sent_by, success=False, error_message=exc)
            raise
        self._log_email(email_type, subject, body, recipient, sent_by=sent_by, success=True)
        return True

    def send_interview_invitation(self, request=None, user=None, subject_template=None, body_template=None):
        if not self.has_invitation_details:
            raise ValueError("Interview date and interview location/link are required before sending an invitation.")
        page_settings = CareerPageSettings.objects.first() or CareerPageSettings()
        subject_template = subject_template or page_settings.interview_email_subject or DEFAULT_INTERVIEW_EMAIL_SUBJECT
        body_template = body_template or page_settings.interview_email_body or DEFAULT_INTERVIEW_EMAIL_BODY
        sent_by = user or getattr(request, "user", None)
        self.send_career_email("interview_invitation", subject_template, body_template, sent_by=sent_by)
        self.status = "interview_invited"
        self.invitation_sent_at = timezone.now()
        self.save(update_fields=["status", "status_updated_at", "invitation_sent_at", "updated_at"])
        return True

    def send_rejection_email(self, request=None, user=None, subject_template=None, body_template=None, rejection_reason=""):
        page_settings = CareerPageSettings.objects.first() or CareerPageSettings()
        subject_template = subject_template or page_settings.rejection_email_subject or DEFAULT_REJECTION_EMAIL_SUBJECT
        body_template = body_template or page_settings.rejection_email_body or DEFAULT_REJECTION_EMAIL_BODY
        sent_by = user or getattr(request, "user", None)
        self.send_career_email(
            "rejection",
            subject_template,
            body_template,
            sent_by=sent_by,
            context_extra={"rejection_reason": rejection_reason},
        )
        self.status = "rejected"
        self.rejection_sent_at = timezone.now()
        self.save(update_fields=["status", "status_updated_at", "rejected_at", "rejection_sent_at", "updated_at"])
        return True



class CareerEmailVerification(TimeStampedModel):
    """Short-lived OTP verification used before public job application submission."""

    job = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name="email_verifications")
    email = models.EmailField(db_index=True)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField(db_index=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    used_at = models.DateTimeField(blank=True, null=True)
    send_count = models.PositiveIntegerField(default=1)
    attempts = models.PositiveIntegerField(default=0)
    sent_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Career Email Verification"
        verbose_name_plural = "Career Email Verifications"
        indexes = [
            models.Index(fields=["job", "email", "expires_at"]),
            models.Index(fields=["verified_at", "used_at"]),
        ]

    def __str__(self):
        return f"{self.email} — {self.job.title}"

    @staticmethod
    def normalize_email(email):
        return (email or "").strip().lower()

    @staticmethod
    def hash_code(email, code):
        normalized = CareerEmailVerification.normalize_email(email)
        return salted_hmac("career-email-verification", f"{normalized}:{code}").hexdigest()

    @classmethod
    def generate_code(cls):
        return get_random_string(6, allowed_chars="0123456789")

    @classmethod
    def create_and_send(cls, job, email, request=None, career_settings=None):
        email = cls.normalize_email(email)
        expiry_minutes = int(getattr(settings, "CAREER_EMAIL_OTP_EXPIRY_MINUTES", 15))
        code = cls.generate_code()
        verification = cls.objects.create(
            job=job,
            email=email,
            code_hash=cls.hash_code(email, code),
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
            sent_ip=(get_client_ip_from_request(request) if request else None),
            user_agent=(request.META.get("HTTP_USER_AGENT", "")[:2000] if request else ""),
        )
        page_settings = career_settings or CareerPageSettings.objects.first() or CareerPageSettings()
        context = {"code": code, "job": job, "email": email, "expiry_minutes": expiry_minutes}
        subject = render_email_template(page_settings.email_verification_subject or DEFAULT_EMAIL_VERIFICATION_SUBJECT, context).replace("\n", " ").strip()
        body = render_email_template(page_settings.email_verification_body or DEFAULT_EMAIL_VERIFICATION_BODY, context)
        send_mail(subject or DEFAULT_EMAIL_VERIFICATION_SUBJECT, body, career_from_email(), [email], fail_silently=False)
        return verification

    @classmethod
    def find_latest(cls, job, email):
        email = cls.normalize_email(email)
        return cls.objects.filter(job=job, email__iexact=email, used_at__isnull=True).order_by("-created_at").first()

    @classmethod
    def find_latest_verified(cls, job, email):
        email = cls.normalize_email(email)
        return cls.objects.filter(
            job=job,
            email__iexact=email,
            verified_at__isnull=False,
            used_at__isnull=True,
            expires_at__gte=timezone.now(),
        ).order_by("-verified_at", "-created_at").first()

    def verify(self, code):
        self.attempts += 1
        now = timezone.now()
        if self.used_at:
            self.save(update_fields=["attempts", "updated_at"])
            return False, "This verification code has already been used. Please request a new code."
        if self.expires_at < now:
            self.save(update_fields=["attempts", "updated_at"])
            return False, "This verification code has expired. Please request a new code."
        max_attempts = int(getattr(settings, "CAREER_EMAIL_OTP_MAX_ATTEMPTS", 6))
        if self.attempts > max_attempts:
            self.save(update_fields=["attempts", "updated_at"])
            return False, "Too many incorrect verification attempts. Please request a new code."
        expected = self.hash_code(self.email, (code or "").strip())
        if not constant_time_compare(expected, self.code_hash):
            self.save(update_fields=["attempts", "updated_at"])
            return False, "The verification code is incorrect."
        self.verified_at = now
        self.save(update_fields=["attempts", "verified_at", "updated_at"])
        return True, "Email verified."

    def mark_used(self):
        self.used_at = timezone.now()
        self.save(update_fields=["used_at", "updated_at"])


class JobApplicationDocument(TimeStampedModel):
    DOCUMENT_TYPES = [
        ("supporting", "Supporting Document"),
        ("certificate", "Certificate / License"),
        ("portfolio", "Portfolio / Project Evidence"),
        ("id", "ID / Iqama Copy"),
        ("other", "Other"),
    ]

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES, default="supporting")
    title = models.CharField(max_length=180, blank=True, default="")
    file = models.FileField(upload_to=application_extra_document_path, validators=[validate_career_document_file], help_text="PDF, DOC or DOCX only.")
    notes = models.TextField(blank=True, default="")
    uploaded_by_applicant = models.BooleanField(default=True)

    class Meta:
        ordering = ["document_type", "id"]
        verbose_name = "Application Document"
        verbose_name_plural = "Application Documents"

    def __str__(self):
        return self.title or self.file.name

class JobApplicationEmailLog(TimeStampedModel):
    EMAIL_TYPES = [
        ("interview_invitation", "Interview Invitation"),
        ("rejection", "Rejection Email"),
        ("custom", "Custom Email"),
    ]

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="email_logs")
    email_type = models.CharField(max_length=40, choices=EMAIL_TYPES, default="custom")
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, default="")
    interview_date = models.DateTimeField(blank=True, null=True)
    interview_mode = models.CharField(max_length=30, blank=True, default="")
    interview_location = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Application Email Log"
        verbose_name_plural = "Application Email Logs"
        indexes = [
            models.Index(fields=["email_type", "created_at"]),
            models.Index(fields=["success", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_email_type_display()} — {self.recipient}"

