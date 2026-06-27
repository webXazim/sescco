from django.contrib import admin, messages
from django.db import IntegrityError
from django.utils.html import format_html


class ProductionAdminSafetyMixin:
    """Reusable admin polish for production CMS records.

    Adds safer bulk actions, timestamp visibility, clear status badges, and friendlier
    duplicate-save feedback. It intentionally avoids changing database schema.
    """

    actions = ("mark_active", "mark_inactive")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request, obj))
        for field in ("created_at", "updated_at"):
            if hasattr(self.model, field) and field not in fields:
                fields.append(field)
        return fields

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not hasattr(self.model, "is_active"):
            actions.pop("mark_active", None)
            actions.pop("mark_inactive", None)
        return actions

    @admin.action(description="Mark selected records active")
    def mark_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} record(s) marked active.", messages.SUCCESS)

    @admin.action(description="Mark selected records inactive")
    def mark_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} record(s) marked inactive.", messages.WARNING)

    @admin.display(description="Status")
    def admin_status_badge(self, obj):
        if hasattr(obj, "is_active") and not obj.is_active:
            return format_html('<span style="color:#8a4b00;font-weight:700;">Inactive</span>')
        if hasattr(obj, "is_published") and not obj.is_published:
            return format_html('<span style="color:#8a4b00;font-weight:700;">Draft</span>')
        return format_html('<span style="color:#087443;font-weight:700;">Live</span>')

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except IntegrityError as exc:
            self.message_user(
                request,
                "This record could not be saved because it would duplicate a protected unique value such as slug, key, or one-to-one relation. Check the slug/key and try again.",
                messages.ERROR,
            )
            raise exc


class SingletonAdminSafetyMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = f"{self.model._meta.verbose_name} — singleton settings"
        return super().changelist_view(request, extra_context=extra_context)
