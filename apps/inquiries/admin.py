from django.contrib import admin
from .models import ContactInquiry, ContactPageSettings, InquirySubject, NewsletterSubscriber


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(ContactPageSettings)
class ContactPageSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Hero", {"fields": ("eyebrow", "hero_title", "hero_subtitle", "hero_image")}),
        ("Intro / form", {"fields": ("intro_title", "intro_text")}),
        ("Email notifications", {"fields": ("notification_email", "email_from_name")}),
        ("Google map", {"fields": ("map_eyebrow", "map_title", "map_subtitle", "google_map_embed_url", "google_map_url", "map_button_text")}),
        ("Visibility", {"fields": ("show_contact_methods", "show_offices", "show_business_hours", "show_map", "show_faqs")}),
    )


@admin.register(InquirySubject)
class InquirySubjectAdmin(admin.ModelAdmin):
    list_display = ("title", "email_to", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "subject", "status", "is_spam_suspected", "created_at")
    list_editable = ("status", "is_spam_suspected")
    list_filter = ("status", "is_spam_suspected", "subject", "created_at")
    search_fields = ("full_name", "email", "phone", "message")
    readonly_fields = ("created_at", "updated_at", "ip_address", "user_agent")
    fieldsets = (
        ("Sender", {"fields": ("full_name", "company_name", "email", "phone")}),
        ("Inquiry", {"fields": ("subject", "subject_text", "message", "consent", "source_page")}),
        ("Management", {"fields": ("status", "is_spam_suspected", "admin_note")}),
        ("Technical", {"fields": ("ip_address", "user_agent")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("email",)
