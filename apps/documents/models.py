from django.db import models
from django.utils.text import slugify
from apps.core.models import OrderedActiveModel, TimeStampedModel


class DocumentCategory(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    icon_text = models.CharField(max_length=40, blank=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name_plural = "Document categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class DownloadDocument(OrderedActiveModel, TimeStampedModel):
    category = models.ForeignKey(DocumentCategory, on_delete=models.SET_NULL, related_name="documents", blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to="documents/files/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="documents/thumbnails/", blank=True, null=True)
    file_type = models.CharField(max_length=40, blank=True, default="PDF")
    file_size = models.CharField(max_length=40, blank=True)
    version = models.CharField(max_length=40, blank=True, default="2024.1")
    published_date = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    requires_request = models.BooleanField(default=False)
    access_level = models.CharField(max_length=30, default="public", choices=[("public", "Public"), ("request", "Request Required"), ("private", "Private")])
    preview_enabled = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class DocumentRequest(TimeStampedModel):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    company = models.CharField(max_length=120, blank=True)
    requested_document = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.requested_document


class DownloadLog(TimeStampedModel):
    document = models.ForeignKey(DownloadDocument, on_delete=models.CASCADE, related_name="logs")
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"Download: {self.document}"


class DownloadsPageSettings(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default="Downloads")
    hero_title = models.CharField(max_length=255, default="Company Profile & Key Documents")
    hero_subtitle = models.TextField(blank=True, default="Access company profiles, certifications, policies and other important documents.")
    hero_image = models.ImageField(upload_to="downloads/page/", blank=True, null=True)
    intro_title = models.CharField(max_length=255, default="Document Center")
    intro_text = models.TextField(blank=True)
    show_category_tabs = models.BooleanField(default=True)
    show_search = models.BooleanField(default=True)
    show_featured_document = models.BooleanField(default=True)
    show_document_table = models.BooleanField(default=True)
    show_request_document = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Downloads Page Settings"
        verbose_name_plural = "Downloads Page Settings"

    def __str__(self):
        return "Downloads Page Settings"


class DocumentPageCTA(TimeStampedModel):
    title = models.CharField(max_length=255, default="Can’t find what you’re looking for?")
    subtitle = models.TextField(blank=True, default="Contact our team and we’ll help you with the document you need.")
    button_text = models.CharField(max_length=120, default="Request a Document")
    button_url = models.CharField(max_length=255, default="/downloads/request/")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Document Page CTA"
        verbose_name_plural = "Document Page CTA"

    def __str__(self):
        return self.title
