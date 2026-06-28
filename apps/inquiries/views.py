from django.contrib import messages
from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import OperationalError, ProgrammingError
from django.shortcuts import redirect, render

from apps.core.models import BusinessHour, CompanyProfile, ContactMethod, OfficeLocation
from apps.pages.models import FAQ
from .forms import ContactInquiryForm
from .models import ContactPageSettings, InquirySubject


CONTACT_CONTEXT_TEXT = {
    "career": {
        "en": {
            "page_title": "Contact HR | SESCCO",
            "meta_description": "Contact SESCCO HR for career questions, job applications and recruitment communication.",
            "side_eyebrow": "Career inquiry",
            "side_title": "Talk to SESCCO HR.",
            "side_text": "For job-related questions, application updates or future opportunities, share your details and HR will respond through the official email channel.",
            "form_eyebrow": "HR inquiry",
            "form_title": "Contact HR",
            "form_text": "Share your career question and our HR team will contact you.",
            "success": "Your HR inquiry has been received. Our team will contact you soon.",
        },
        "ar": {
            "page_title": "تواصل مع الموارد البشرية | SESCCO",
            "meta_description": "تواصل مع الموارد البشرية في SESCCO بخصوص الوظائف وطلبات التوظيف.",
            "side_eyebrow": "استفسار وظيفي",
            "side_title": "تواصل مع الموارد البشرية.",
            "side_text": "للاستفسارات الوظيفية أو تحديثات الطلبات أو الفرص المستقبلية، شارك بياناتك وسيتواصل معك فريق الموارد البشرية عبر البريد الرسمي.",
            "form_eyebrow": "استفسار موارد بشرية",
            "form_title": "تواصل مع الموارد البشرية",
            "form_text": "شارك استفسارك الوظيفي وسيتواصل معك فريق الموارد البشرية.",
            "success": "تم استلام استفسارك الوظيفي. سيتواصل معك فريقنا قريباً.",
        },
        "zh-hans": {
            "page_title": "联系人力资源 | SESCCO",
            "meta_description": "联系 SESCCO 人力资源团队，咨询职位、申请和招聘沟通。",
            "side_eyebrow": "招聘咨询",
            "side_title": "联系 SESCCO 人力资源。",
            "side_text": "如有职位咨询、申请更新或未来机会问题，请提交信息，人力资源团队将通过官方邮箱联系您。",
            "form_eyebrow": "人力资源咨询",
            "form_title": "联系人力资源",
            "form_text": "请说明您的招聘问题，我们的人力资源团队会与您联系。",
            "success": "您的招聘咨询已收到。我们的团队会尽快联系您。",
        },
    },
    "default": {
        "en": {
            "page_title": "Contact SESCCO",
            "meta_description": "Contact Summit Engineering Solutions Contracting Co. for electrical, civil, fitout and contract support inquiries in Saudi Arabia.",
            "side_eyebrow": "Project inquiry",
            "form_eyebrow": "New inquiry",
            "form_title": "Send Us an Inquiry",
            "form_text": "Share your requirement and our team will contact you.",
            "success": "Your inquiry has been received. Our team will contact you soon.",
        },
        "ar": {
            "page_title": "اتصل بنا | SESCCO",
            "meta_description": "تواصل مع SESCCO لاستفسارات الهندسة والمشاريع والدعم في السعودية.",
            "side_eyebrow": "استفسار مشروع",
            "form_eyebrow": "استفسار جديد",
            "form_title": "أرسل استفسارك",
            "form_text": "املأ النموذج وسيقوم فريقنا بالتواصل معك.",
            "success": "تم استلام استفسارك. سيتواصل معك فريقنا قريباً.",
        },
        "zh-hans": {
            "page_title": "联系 SESCCO",
            "meta_description": "联系 SESCCO 咨询沙特阿拉伯的工程、项目和支持服务。",
            "side_eyebrow": "项目咨询",
            "form_eyebrow": "新的咨询",
            "form_title": "发送咨询",
            "form_text": "请填写下面的表格，我们的团队会尽快与您联系。",
            "success": "您的咨询已收到。我们的团队会尽快联系您。",
        },
    },
}


def _contact_settings_value(contact_settings, field_name, default=""):
    try:
        return getattr(contact_settings, field_name)
    except (OperationalError, ProgrammingError):
        return default


def _contact_notification_recipient(inquiry, contact_settings):
    if inquiry.subject and inquiry.subject.email_to:
        return inquiry.subject.email_to
    notification_email = _contact_settings_value(contact_settings, "notification_email")
    if notification_email:
        return notification_email
    company = CompanyProfile.objects.first()
    if company and company.email_primary:
        return company.email_primary
    return getattr(django_settings, "SERVER_EMAIL", None) or getattr(django_settings, "DEFAULT_FROM_EMAIL", "")


def _contact_notification_from_email(contact_settings):
    from_email = getattr(django_settings, "DEFAULT_FROM_EMAIL", None) or getattr(django_settings, "SERVER_EMAIL", None)
    email_from_name = _contact_settings_value(contact_settings, "email_from_name", "SESCCO Website")
    if email_from_name and from_email:
        return f"{email_from_name} <{from_email}>"
    return from_email


def _send_contact_notification(request, inquiry, contact_settings):
    recipient = _contact_notification_recipient(inquiry, contact_settings)
    if not recipient:
        return

    subject_label = inquiry.subject.title if inquiry.subject else inquiry.subject_text or "General inquiry"
    email_subject = f"New SESCCO inquiry: {subject_label}"
    admin_url = ""
    if request:
        try:
            admin_url = request.build_absolute_uri(f"/admin/inquiries/contactinquiry/{inquiry.pk}/change/")
        except Exception:
            admin_url = f"/admin/inquiries/contactinquiry/{inquiry.pk}/change/"

    body = "\n".join(
        [
            "A new contact inquiry was submitted from the SESCCO website.",
            "",
            f"Name: {inquiry.full_name}",
            f"Company: {inquiry.company_name or '-'}",
            f"Email: {inquiry.email or '-'}",
            f"Phone: {inquiry.phone or '-'}",
            f"Subject: {subject_label}",
            f"Consent: {'Yes' if inquiry.consent else 'No'}",
            f"Source page: {inquiry.source_page or '-'}",
            f"IP address: {inquiry.ip_address or '-'}",
            "",
            "Message:",
            inquiry.message,
            "",
            f"Open in admin: {admin_url}" if admin_url else "",
        ]
    ).strip()

    send_mail(
        email_subject,
        body,
        _contact_notification_from_email(contact_settings),
        [recipient],
        fail_silently=False,
    )


def _contact_context(request):
    raw_context = (request.GET.get("type") or request.GET.get("context") or "").strip().lower()
    context_type = "career" if raw_context in {"career", "hr", "job", "jobs", "recruitment"} else "default"
    lang = getattr(request, "LANGUAGE_CODE", "en") or "en"
    text_group = CONTACT_CONTEXT_TEXT[context_type]
    text = text_group.get(lang, text_group["en"])
    return context_type, text


def _career_subject_initial():
    try:
        return InquirySubject.objects.filter(title__iexact="Career / HR Inquiry", is_active=True).first()
    except (OperationalError, ProgrammingError):
        return None


def contact(request):
    settings = ContactPageSettings.objects.defer("notification_email", "email_from_name").first() or ContactPageSettings()
    context_type, contact_context_text = _contact_context(request)
    form_kwargs = {"contact_context": context_type}
    if context_type == "career":
        career_subject = _career_subject_initial()
        if career_subject:
            form_kwargs["initial"] = {"subject": career_subject}

    if request.method == "POST":
        form = ContactInquiryForm(request.POST, **form_kwargs)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.source_page = request.META.get("HTTP_REFERER", "")
            inquiry.ip_address = request.META.get("REMOTE_ADDR")
            inquiry.user_agent = request.META.get("HTTP_USER_AGENT", "")
            # Basic spam signal only. Do not block; mark for admin review.
            if len(inquiry.message or "") < 10:
                inquiry.is_spam_suspected = True
            inquiry.save()
            try:
                _send_contact_notification(request, inquiry, settings)
            except Exception:
                # Keep the public form reliable even if SMTP is temporarily unavailable.
                pass
            messages.success(request, contact_context_text["success"])
            return redirect(request.get_full_path())
    else:
        form = ContactInquiryForm(**form_kwargs)

    office_locations = OfficeLocation.objects.filter(is_active=True).order_by("-is_primary", "sort_order", "id")
    primary_office = office_locations.first()
    office_count = office_locations.count()
    show_offices_section = office_count > 1 or request.user.is_staff
    only_primary_office_preview = office_count == 1 and request.user.is_staff
    contact_methods = ContactMethod.objects.filter(is_active=True, show_on_contact_page=True).order_by("sort_order", "id")
    business_hours = BusinessHour.objects.filter(is_active=True).order_by("sort_order", "id")

    contact_map_embed_url = settings.google_map_embed_url or (primary_office.map_embed_url if primary_office else "")
    contact_map_url = settings.google_map_url or (primary_office.map_url if primary_office else "")

    faqs = FAQ.objects.filter(is_active=True)[:4]
    is_staff = request.user.is_authenticated and request.user.is_staff
    show_contact_methods_section = settings.show_contact_methods and (contact_methods.exists() or is_staff)
    show_business_hours_section = settings.show_business_hours and (business_hours.exists() or is_staff)
    show_map_section = settings.show_map and (bool(contact_map_embed_url) or is_staff)
    show_faqs_section = settings.show_faqs and (faqs.exists() or is_staff)
    return render(
        request,
        "inquiries/contact.html",
        {
            "form": form,
            "faqs": faqs,
            "contact_settings": settings,
            "office_locations": office_locations,
            "primary_office": primary_office,
            "show_offices_section": show_offices_section,
            "only_primary_office_preview": only_primary_office_preview,
            "contact_methods": contact_methods,
            "business_hours": business_hours,
            "contact_map_embed_url": contact_map_embed_url,
            "contact_map_url": contact_map_url,
            "show_contact_methods_section": show_contact_methods_section,
            "show_business_hours_section": show_business_hours_section,
            "show_map_section": show_map_section,
            "show_faqs_section": show_faqs_section,
            "contact_context_type": context_type,
            "contact_context": contact_context_text,
            "meta_title": contact_context_text["page_title"],
            "meta_description": contact_context_text["meta_description"],
        },
    )
