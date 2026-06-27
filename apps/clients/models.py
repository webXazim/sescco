from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from apps.core.models import OrderedActiveModel, TimeStampedModel


class Client(OrderedActiveModel, TimeStampedModel):
    category_ref = models.ForeignKey('ClientCategory', on_delete=models.SET_NULL, blank=True, null=True, related_name='clients')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="clients/logos/", blank=True, null=True)
    website = models.URLField(blank=True)
    category = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Partner(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="partners/logos/", blank=True, null=True)
    website = models.URLField(blank=True)
    partner_tier = models.CharField(max_length=120, blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Project contractor"
        verbose_name_plural = "Project contractors"

    def __str__(self):
        return self.name


class Certificate(OrderedActiveModel, TimeStampedModel):
    category_ref = models.ForeignKey('CertificateCategory', on_delete=models.SET_NULL, blank=True, null=True, related_name='certificates')
    title = models.CharField(max_length=255)
    certificate_type = models.CharField(max_length=120, blank=True)
    issuer = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True, default="", help_text="Short public description shown in the certificate modal.")
    certificate_number = models.CharField(max_length=120, blank=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to="certificates/images/", blank=True, null=True)
    file = models.FileField(upload_to="certificates/files/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    @property
    def is_expired(self):
        from django.utils import timezone
        return bool(self.expiry_date and self.expiry_date < timezone.localdate())

    def __str__(self):
        return self.title


class Accreditation(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="accreditations/", blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Standard(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=255)
    icon_text = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Testimonial(OrderedActiveModel, TimeStampedModel):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, blank=True, null=True)
    quote = CKEditor5Field(config_name="extends")
    person_name = models.CharField(max_length=255, blank=True)
    person_designation = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.person_name or "Testimonial"


class TrustPageSettings(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default="Certifications & Clients")
    hero_title = models.CharField(max_length=255, default="Certifications and clients.")
    hero_subtitle = models.TextField(blank=True, default="Review SESCCO certificates first, then the client organizations connected to our project experience.")
    hero_image = models.ImageField(upload_to="trust-page/hero/", blank=True, null=True)

    clients_eyebrow = models.CharField(max_length=120, default="Our Key Clients")
    clients_title = models.CharField(max_length=255, default="Trusted by respected organizations.")
    partners_eyebrow = models.CharField(max_length=120, default="Project Network")
    partners_title = models.CharField(max_length=255, default="Project contractors only for project detail records.")
    certificates_eyebrow = models.CharField(max_length=120, default="Our Certifications")
    certificates_title = models.CharField(max_length=255, default="Certified systems and operational excellence.")
    standards_eyebrow = models.CharField(max_length=120, default="Compliance & Standards")
    standards_title = models.CharField(max_length=255, default="Standards we follow.")
    testimonials_eyebrow = models.CharField(max_length=120, default="Testimonials")
    testimonials_title = models.CharField(max_length=255, default="What clients say about us.")

    show_clients = models.BooleanField(default=True)
    show_partners = models.BooleanField(default=False)
    show_certificates = models.BooleanField(default=True)
    show_accreditations = models.BooleanField(default=True)
    show_standards = models.BooleanField(default=True)
    show_testimonials = models.BooleanField(default=True)
    show_documents = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Trust Page Settings"
        verbose_name_plural = "Trust Page Settings"

    def __str__(self):
        return "Trust Page Settings"


class TrustMetric(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    icon_text = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.value} {self.title}"


class ClientCategory(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name_plural = "Client categories"

    class Meta(OrderedActiveModel.Meta):
        verbose_name = "Project contractor"
        verbose_name_plural = "Project contractors"

    def __str__(self):
        return self.name


class CertificateCategory(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name_plural = "Certificate categories"

    def __str__(self):
        return self.name


class ComplianceBlock(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title
