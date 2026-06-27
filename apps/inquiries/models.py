from django.db import models
from apps.core.models import OrderedActiveModel, TimeStampedModel


class InquirySubject(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    email_to = models.EmailField(blank=True)

    def __str__(self):
        return self.title


class ContactInquiry(TimeStampedModel):
    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("responded", "Responded"),
        ("resolved", "Resolved"),
        ("spam", "Spam"),
        ("archived", "Archived"),
    ]
    full_name = models.CharField(max_length=120)
    company_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    subject = models.ForeignKey(InquirySubject, on_delete=models.SET_NULL, blank=True, null=True)
    subject_text = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    consent = models.BooleanField(default=False)
    source_page = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    admin_note = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    is_spam_suspected = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.subject or self.subject_text}"


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class ContactPageSettings(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default="Contact Us")
    hero_title = models.CharField(max_length=255, default="Contact Us. We’re Here to Help.")
    hero_subtitle = models.TextField(blank=True, default="Have a question, need a quote or ready to start your next project? Our team is ready to listen.")
    hero_image = models.ImageField(upload_to="contact/page/", blank=True, null=True)
    intro_title = models.CharField(max_length=255, default="Let’s Build Something Great Together")
    intro_text = models.TextField(blank=True, default="Reach out to us for project inquiries, collaborations or support. We’ll get back to you promptly.")
    notification_email = models.EmailField(
        blank=True,
        default="info@sescco.com",
        help_text="Default email address that receives contact form submissions. Subject-specific email_to overrides this when set.",
    )
    email_from_name = models.CharField(max_length=120, blank=True, default="SESCCO Website")
    map_eyebrow = models.CharField(max_length=120, default="Find Us")
    map_title = models.CharField(max_length=255, default="Visit our office location.")
    map_subtitle = models.TextField(blank=True, default="Use the map below to view SESCCO’s office location and open directions in Google Maps.")
    google_map_embed_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Paste a Google Maps embed URL. Example: https://www.google.com/maps?q=Dammam%2C%20Saudi%20Arabia&output=embed",
    )
    google_map_url = models.URLField(
        max_length=1000,
        blank=True,
        help_text="Paste the public Google Maps location/directions URL used by the Get Directions button.",
    )
    map_button_text = models.CharField(max_length=120, default="Open in Google Maps")
    show_contact_methods = models.BooleanField(default=True)
    show_offices = models.BooleanField(default=True)
    show_business_hours = models.BooleanField(default=True)
    show_map = models.BooleanField(default=True)
    show_faqs = models.BooleanField(default=True)
    show_whatsapp_cta = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Contact Page Settings"
        verbose_name_plural = "Contact Page Settings"

    def __str__(self):
        return "Contact Page Settings"
