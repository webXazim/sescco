from django.contrib import admin
from apps.core.admin_safety import ProductionAdminSafetyMixin, SingletonAdminSafetyMixin
from django.utils.html import format_html
from .models import (
    Accreditation, Certificate, CertificateCategory, Client, ClientCategory,
    ComplianceBlock, Partner, Standard, Testimonial, TrustMetric, TrustPageSettings
)


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(TrustPageSettings)
class TrustPageSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Hero", {"fields": ("eyebrow", "hero_title", "hero_subtitle", "hero_image")}),
        ("Certificates Section", {"fields": ("show_certificates", "certificates_eyebrow", "certificates_title")}),
        ("Clients Section", {"fields": ("show_clients", "clients_eyebrow", "clients_title")}),
        ("Other Sections", {"fields": ("show_accreditations", "show_standards", "standards_eyebrow", "standards_title", "show_testimonials", "testimonials_eyebrow", "testimonials_title", "show_documents")}),
    )


@admin.register(ClientCategory)
class ClientCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CertificateCategory)
class CertificateCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Client)
class ClientAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("admin_logo_preview", "name", "category_ref", "category", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("category_ref", "category", "is_featured", "is_active")
    search_fields = ("name", "category", "description")
    fieldsets = (
        ("Client Content", {"fields": ("name", "description", "category_ref", "category")}),
        ("Logo", {"fields": ("logo", "admin_logo_preview"), "description": "Upload the client logo here. Recommended transparent PNG or SVG for best result."}),
        ("Display", {"fields": ("is_featured", "sort_order", "is_active")}),
    )
    readonly_fields = ("admin_logo_preview",)

    @admin.display(description="Logo")
    def admin_logo_preview(self, obj):
        if obj and obj.logo:
            return format_html('<img src="{}" style="width:82px;height:56px;object-fit:contain;background:#fff;border-radius:10px;padding:6px;border:1px solid #dbe7fb;" alt="" />', obj.logo.url)
        return "—"


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    verbose_name = "Project contractor"
    verbose_name_plural = "Project contractors"
    list_display = ("name", "partner_tier", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    search_fields = ("name", "partner_tier")


@admin.register(Certificate)
class CertificateAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("admin_preview", "title", "category_ref", "issuer", "expiry_date", "is_expired", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("category_ref", "issuer", "certificate_type", "is_featured", "is_active")
    search_fields = ("title", "issuer", "certificate_number", "description")
    fieldsets = (
        ("Certificate Content", {"fields": ("title", "description", "certificate_type", "category_ref", "issuer", "certificate_number")}),
        ("Media", {"fields": ("image", "file")}),
        ("Dates", {"fields": ("issue_date", "expiry_date")}),
        ("Display", {"fields": ("is_featured", "sort_order", "is_active")}),
    )
    readonly_fields = ("admin_preview",)

    @admin.display(description="Preview")
    def admin_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:58px;height:72px;object-fit:cover;border-radius:8px;border:1px solid #dbe7fb;" alt="" />', obj.image.url)
        return "—"


@admin.register(Accreditation)
class AccreditationAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "description")


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "description")


@admin.register(ComplianceBlock)
class ComplianceBlockAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "description")


@admin.register(TrustMetric)
class TrustMetricAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "value", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "value", "description")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("person_name", "client", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("client", "is_featured", "is_active")
    search_fields = ("person_name", "person_designation", "quote")
