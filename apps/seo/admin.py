from django.contrib import admin
from .models import RedirectRule, RobotsSettings, SchemaMarkup


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(RobotsSettings)
class RobotsSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    pass


@admin.register(RedirectRule)
class RedirectRuleAdmin(admin.ModelAdmin):
    list_display = ("old_path", "new_path", "permanent", "is_active")
    list_editable = ("permanent", "is_active")
    search_fields = ("old_path", "new_path")


@admin.register(SchemaMarkup)
class SchemaMarkupAdmin(admin.ModelAdmin):
    list_display = ("title", "page_path", "is_active")
    list_editable = ("is_active",)
    search_fields = ("title", "page_path", "json_ld")
