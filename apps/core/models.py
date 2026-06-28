from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
from .translation_registry import content_type_choices


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderedActiveModel(models.Model):
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ["sort_order", "id"]


class CompanyProfile(TimeStampedModel):
    company_name = models.CharField(max_length=255, default="Summit Engineering Solutions Contracting Co.")
    short_name = models.CharField(max_length=80, default="SESCCO")
    tagline = models.CharField(max_length=255, default="Where high-quality engineering meets reliable service.")
    description = CKEditor5Field(blank=True, config_name="extends")
    logo = models.ImageField(upload_to="branding/", blank=True, null=True)
    favicon = models.ImageField(upload_to="branding/", blank=True, null=True)
    established_year = models.PositiveIntegerField(default=2015)
    aramco_vendor_code = models.CharField(max_length=80, blank=True, default="10114560")
    sec_vendor_code = models.CharField(max_length=80, blank=True, default="02013075")
    phone_primary = models.CharField(max_length=50, blank=True, default="")
    phone_secondary = models.CharField(max_length=50, blank=True, default="")
    email_primary = models.EmailField(blank=True, default="info@sescco.com")
    email_secondary = models.EmailField(blank=True, default="imran@sescco.com")
    email_third = models.EmailField(blank=True, default="mehrab@sescco.com")
    address = models.CharField(max_length=255, blank=True, default="Dammam, Saudi Arabia")
    city = models.CharField(max_length=120, blank=True, default="Dammam")
    country = models.CharField(max_length=120, blank=True, default="Saudi Arabia")
    website_url = models.URLField(blank=True, default="https://sescco.com")
    map_embed_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profile"

    def __str__(self):
        return self.short_name


class SiteSettings(TimeStampedModel):
    site_name = models.CharField(max_length=255, default="SESCCO")
    domain = models.CharField(max_length=255, default="sescco.com")
    default_language = models.CharField(max_length=10, default="en")
    enable_multilingual = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)
    default_seo_title = models.CharField(max_length=255, blank=True)
    default_seo_description = models.TextField(blank=True)
    default_og_image = models.ImageField(upload_to="seo/", blank=True, null=True)
    footer_social_title = models.CharField(max_length=120, default="Find us on social media")
    show_developer_credit = models.BooleanField(default=True)
    developer_credit_label = models.CharField(max_length=120, default="Website developed by")
    developer_name = models.CharField(max_length=120, default="A2TDEV")
    developer_url = models.URLField(blank=True, default="https://a2tdev.com")
    developer_seo_description = models.CharField(max_length=255, blank=True, default="Professional website design and development partner for SESCCO.")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name


class ThemeSettings(TimeStampedModel):
    primary_color = models.CharField(max_length=20, default="#0758d8")
    secondary_color = models.CharField(max_length=20, default="#042a5f")
    accent_color = models.CharField(max_length=20, default="#00a6df")
    dark_color = models.CharField(max_length=20, default="#061a34")
    light_color = models.CharField(max_length=20, default="#f4f8fd")
    header_style = models.CharField(max_length=50, default="standard")
    footer_style = models.CharField(max_length=50, default="standard")
    button_style = models.CharField(max_length=50, default="rounded")

    class Meta:
        verbose_name = "Theme Settings"
        verbose_name_plural = "Theme Settings"

    def __str__(self):
        return "Theme Settings"


class NavigationMenu(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    url = models.CharField(max_length=255)
    open_in_new_tab = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class FooterColumn(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title


class FooterLink(OrderedActiveModel, TimeStampedModel):
    column = models.ForeignKey(FooterColumn, on_delete=models.CASCADE, related_name="links")
    title = models.CharField(max_length=120)
    url = models.CharField(max_length=255)
    open_in_new_tab = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class CTASettings(TimeStampedModel):
    header_cta_text = models.CharField(max_length=80, default="Get in Touch")
    header_cta_url = models.CharField(max_length=255, default="/contact/")
    main_cta_title = models.CharField(max_length=255, default="Let’s Build Something Great Together.")
    main_cta_subtitle = models.CharField(max_length=255, default="Ready to start your next project? Our team is here to help.")
    main_cta_button_text = models.CharField(max_length=80, default="Get in Touch Today")
    main_cta_button_url = models.CharField(max_length=255, default="/contact/")

    class Meta:
        verbose_name = "CTA Settings"
        verbose_name_plural = "CTA Settings"

    def __str__(self):
        return "CTA Settings"


class SocialLink(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=80)
    url = models.URLField()
    icon_text = models.CharField(max_length=20, blank=True, help_text="Example: in, f, X")

    def __str__(self):
        return self.title


class SiteAsset(OrderedActiveModel, TimeStampedModel):
    ASSET_TYPES = [
        ("hero", "Hero Background"),
        ("about", "About Image"),
        ("pattern", "Pattern / Decoration"),
        ("footer", "Footer Graphic"),
        ("placeholder", "Placeholder"),
    ]
    title = models.CharField(max_length=120)
    asset_type = models.CharField(max_length=40, choices=ASSET_TYPES, default="placeholder")
    image = models.ImageField(upload_to="site-assets/")
    alt_text = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class TrustMetric(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    icon_image = models.ImageField(
        upload_to="trust/metric-icons/",
        blank=True,
        null=True,
        help_text=(
            "Optional square icon image. Recommended upload size: 96 x 96 px "
            "PNG/WebP/JPG. It renders as 32 x 32 px inside the premium 64 x 64 px metric badge."
        ),
    )
    icon_text = models.CharField(
        max_length=40,
        blank=True,
        help_text="Fallback icon when no image is uploaded. Use one clean icon character such as ✓, 🛡, ✦, or an emoji. HTML is not required.",
    )
    description = models.CharField(max_length=255, blank=True)
    show_on_home = models.BooleanField(default=True)
    show_on_about = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}: {self.value}"


class CTASection(OrderedActiveModel, TimeStampedModel):
    key = models.SlugField(unique=True, help_text="Example: global-main, homepage, services, contact")
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True)
    button_text = models.CharField(max_length=120, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    background_image = models.ImageField(upload_to="cta/", blank=True, null=True)
    style = models.CharField(max_length=80, default="blue")

    def __str__(self):
        return self.title


class OfficeLocation(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=120, default="Head Office")
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120, blank=True)
    country = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    map_url = models.URLField(blank=True)
    map_embed_url = models.URLField(blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class BusinessHour(OrderedActiveModel, TimeStampedModel):
    day_label = models.CharField(max_length=80)
    hours = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.day_label}: {self.hours}"


class ContactMethod(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    value = models.CharField(max_length=255)
    icon_text = models.CharField(max_length=40, blank=True)
    url = models.CharField(max_length=255, blank=True)
    show_on_contact_page = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True)

    def __str__(self):
        return self.title


TRANSLATION_CONTENT_TYPE_CHOICES = content_type_choices()


class LocalizedContent(TimeStampedModel):
    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("ar", "Arabic"),
        ("zh-hans", "Chinese"),
    ]
    content_type = models.CharField(max_length=120, choices=TRANSLATION_CONTENT_TYPE_CHOICES, help_text="Select which type of content this translation belongs to.")
    object_id = models.PositiveIntegerField()
    language_code = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    field_name = models.CharField(max_length=120, help_text="Example: title, body, short_description")
    text = CKEditor5Field(blank=True, config_name="extends")

    class Meta:
        unique_together = ("content_type", "object_id", "language_code", "field_name")
        ordering = ["content_type", "object_id", "language_code", "field_name"]
        verbose_name = "Localized Content Override"
        verbose_name_plural = "Localized Content Overrides"

    def __str__(self):
        return f"{self.content_type}:{self.object_id}:{self.language_code}:{self.field_name}"
