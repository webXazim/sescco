from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("action", "module", "object_title", "user", "created_at")
    list_filter = ("module", "action", "created_at")
    search_fields = ("action", "module", "object_title", "description")
    readonly_fields = ("user", "action", "module", "object_title", "description", "ip_address", "created_at", "updated_at")
