from django.contrib import admin
from apps.core.admin_safety import ProductionAdminSafetyMixin, SingletonAdminSafetyMixin
from django.urls import reverse
from django.utils.html import format_html
from .forms import LocalizedContentAdminForm
from .translation_registry import get_target
from .models import (
    BusinessHour, CompanyProfile, ContactMethod, CTASection, CTASettings,
    FooterColumn, FooterLink, NavigationMenu, OfficeLocation, SiteAsset,
    SiteSettings, SocialLink, ThemeSettings, TrustMetric, LocalizedContent
)


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(CompanyProfile)
class CompanyProfileAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Brand", {"fields": ("company_name", "short_name", "tagline", "description", "logo", "favicon")}),
        ("Trust Codes", {"fields": ("established_year", "aramco_vendor_code", "sec_vendor_code")}),
        ("Contact", {"fields": ("phone_primary", "phone_secondary", "email_primary", "email_secondary", "email_third", "address", "city", "country", "website_url", "map_embed_url")}),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Site", {"fields": ("site_name", "domain", "default_language", "enable_multilingual", "maintenance_mode")}),
        ("SEO Defaults", {"fields": ("default_seo_title", "default_seo_description", "default_og_image")}),
        ("Footer social title", {"fields": ("footer_social_title",)}),
        (
            "Developer credit",
            {
                "fields": (
                    "show_developer_credit",
                    "developer_credit_label",
                    "developer_name",
                    "developer_url",
                    "developer_seo_description",
                ),
                "description": "Shown as a small professional footer credit and included in structured data as the site creator.",
            },
        ),
    )


@admin.register(ThemeSettings)
class ThemeSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    list_display = ("primary_color", "secondary_color", "accent_color", "header_style", "footer_style")


@admin.register(CTASettings)
class CTASettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Header CTA", {"fields": ("header_cta_text", "header_cta_url")}),
        ("Main CTA", {"fields": ("main_cta_title", "main_cta_subtitle", "main_cta_button_text", "main_cta_button_url")}),
    )


@admin.register(NavigationMenu)
class NavigationMenuAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "url", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "url")


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 1


@admin.register(FooterColumn)
class FooterColumnAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    inlines = [FooterLinkInline]


@admin.register(SocialLink)
class SocialLinkAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "url", "icon_text", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")


@admin.register(SiteAsset)
class SiteAssetAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "asset_type", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("asset_type", "is_active")
    search_fields = ("title", "alt_text")


@admin.register(TrustMetric)
class TrustMetricAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("icon_preview", "title", "value", "show_on_home", "show_on_about", "sort_order", "is_active")
    list_editable = ("show_on_home", "show_on_about", "sort_order", "is_active")
    search_fields = ("title", "value", "description", "icon_text")
    readonly_fields = ("icon_preview",)
    fieldsets = (
        ("Metric", {"fields": ("title", "value", "description")}),
        (
            "Icon",
            {
                "fields": ("icon_preview", "icon_image", "icon_text"),
                "description": (
                    "Use either an uploaded square icon image or a text icon. "
                    "Uploaded image takes priority. Recommended upload: 96 x 96 px PNG/WebP/JPG; "
                    "front-end display: 32 x 32 px inside the premium 64 x 64 px metric badge."
                ),
            },
        ),
        ("Display", {"fields": ("show_on_home", "show_on_about", "sort_order", "is_active")}),
    )

    @admin.display(description="Icon")
    def icon_preview(self, obj):
        if obj and obj.icon_image:
            return format_html(
                '<img src="{}" alt="" style="width:32px;height:32px;object-fit:contain;border-radius:8px;" />',
                obj.icon_image.url,
            )
        if obj and obj.icon_text:
            return obj.icon_text
        return "✦"


@admin.register(CTASection)
class CTASectionAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("key", "title", "button_text", "style", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("key", "title", "subtitle")
    prepopulated_fields = {"key": ("title",)}


@admin.register(OfficeLocation)
class OfficeLocationAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("name", "city", "country", "phone", "email", "is_primary", "sort_order", "is_active")
    list_editable = ("is_primary", "sort_order", "is_active")
    search_fields = ("name", "address", "city", "country")


@admin.register(BusinessHour)
class BusinessHourAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("day_label", "hours", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")


@admin.register(ContactMethod)
class ContactMethodAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "value", "show_on_contact_page", "show_in_footer", "sort_order", "is_active")
    list_editable = ("show_on_contact_page", "show_in_footer", "sort_order", "is_active")
    search_fields = ("title", "value")


@admin.register(LocalizedContent)
class LocalizedContentAdmin(admin.ModelAdmin):
    form = LocalizedContentAdminForm
    list_display = ("content_label", "object_id", "language_code", "field_name", "text_preview", "updated_at")
    list_filter = ("content_type", "language_code", "field_name")
    search_fields = ("content_type", "field_name", "text")
    list_editable = ("language_code", "field_name")
    actions = ["duplicate_to_arabic", "duplicate_to_chinese"]

    fieldsets = (
        ("Target", {"fields": ("content_type", "object_id", "language_code", "field_name")}),
        ("Translation", {"fields": ("text",)}),
    )

    def content_label(self, obj):
        target = get_target(obj.content_type)
        return target.model_label if target else obj.content_type
    content_label.short_description = "Content Type"

    def text_preview(self, obj):
        value = str(obj.text or "")
        return value[:80] + ("..." if len(value) > 80 else "")
    text_preview.short_description = "Translation Preview"

    def _duplicate(self, request, queryset, language_code):
        created = 0
        for obj in queryset:
            if obj.language_code == language_code:
                continue
            _, was_created = LocalizedContent.objects.get_or_create(
                content_type=obj.content_type,
                object_id=obj.object_id,
                language_code=language_code,
                field_name=obj.field_name,
                defaults={"text": obj.text},
            )
            if was_created:
                created += 1
        self.message_user(request, f"Created {created} translation draft(s).")

    @admin.action(description="Duplicate selected translations to Arabic as drafts")
    def duplicate_to_arabic(self, request, queryset):
        self._duplicate(request, queryset, "ar")

    @admin.action(description="Duplicate selected translations to Chinese as drafts")
    def duplicate_to_chinese(self, request, queryset):
        self._duplicate(request, queryset, "zh-hans")


def localized_content_count(model_name, language_code):
    return LocalizedContent.objects.filter(content_type=model_name, language_code=language_code).count()

# Upgrade 27 note: Official SESCCO logo is stored in CompanyProfile.logo and used sitewide.


# Upgrade 62: make the Django admin easier to navigate for non-technical site admins.
admin.site.site_header = "SESCCO Administration"
admin.site.site_title = "SESCCO Admin"
admin.site.index_title = "Website content map"
