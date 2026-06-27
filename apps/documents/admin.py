from django.contrib import admin
from apps.core.admin_safety import ProductionAdminSafetyMixin, SingletonAdminSafetyMixin
from django.utils.html import format_html
from .models import DocumentCategory, DocumentPageCTA, DocumentRequest, DownloadDocument, DownloadLog


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()



@admin.register(DocumentPageCTA)
class DocumentPageCTAAdmin(SingletonAdminMixin, admin.ModelAdmin):
    list_display = ("title", "button_text", "button_url", "is_active")


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(DownloadDocument)
class DownloadDocumentAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("admin_file_status", "title", "category", "file_type", "version", "access_level", "is_featured", "is_public", "download_count", "sort_order", "is_active")
    list_editable = ("access_level", "is_featured", "is_public", "sort_order", "is_active")
    list_filter = ("category", "file_type", "access_level", "is_featured", "is_public", "is_active")
    search_fields = ("title", "description", "file_type", "version")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Document content", {"fields": ("title", "slug", "category", "description")}),
        ("Upload file", {"fields": ("file", "thumbnail", "file_type", "file_size", "version", "published_date", "admin_file_status")}),
        ("Public access", {"fields": ("is_public", "access_level", "requires_request", "preview_enabled"), "description": "Use Public for direct download. Use Request Required for sensitive official documents that should not download publicly."}),
        ("Display", {"fields": ("is_featured", "sort_order", "is_active")}),
        ("Stats", {"fields": ("download_count",)}),
    )
    readonly_fields = ("download_count", "admin_file_status")

    @admin.display(description="File")
    def admin_file_status(self, obj):
        if obj and obj.file:
            return format_html('<a href="{}" target="_blank" style="font-weight:700;">Uploaded file</a>', obj.file.url)
        return format_html('<span style="color:#b45309;font-weight:700;">No file uploaded yet</span>')


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = ("requested_document", "name", "email", "phone", "company", "is_resolved", "created_at")
    list_editable = ("is_resolved",)
    list_filter = ("is_resolved", "created_at")
    search_fields = ("requested_document", "name", "email", "phone", "company", "message")


@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ("document", "ip_address", "created_at")
    readonly_fields = ("document", "ip_address", "user_agent", "created_at")
