from django.contrib import messages
from django.conf import settings as django_settings
from django.core.mail import send_mail
from django.db import OperationalError, ProgrammingError
from django.shortcuts import redirect, render

from apps.core.models import BusinessHour, CompanyProfile, ContactMethod, OfficeLocation
from apps.pages.models import FAQ
from .forms import ContactInquiryForm
from .models import ContactPageSettings


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


def contact(request):
    settings = ContactPageSettings.objects.defer("notification_email", "email_from_name").first() or ContactPageSettings()

    if request.method == "POST":
        form = ContactInquiryForm(request.POST)
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
            messages.success(request, "Your inquiry has been received. Our team will contact you soon.")
            return redirect("contact")
    else:
        form = ContactInquiryForm()

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
            "meta_title": "Contact SESCCO",
            "meta_description": "Contact Summit Engineering Solutions Contracting Co. for electrical, civil, fitout and contract support inquiries in Saudi Arabia.",
        },
    )
