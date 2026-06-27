from django.contrib import admin
from apps.core.admin_safety import ProductionAdminSafetyMixin, SingletonAdminSafetyMixin
from .models import Service, ServiceCategory, ServiceCTA, ServiceDeliverable, ServiceDetailPageSettings, ServiceFAQ, ServiceFeature, ServiceKeyPoint, ServiceListFAQ, ServiceListPageSettings, ServiceListProcessStep, ServiceProcessStep




class ServiceKeyPointInline(admin.TabularInline):
    model = ServiceKeyPoint
    extra = 0


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 0


class ServiceCTAInline(admin.StackedInline):
    model = ServiceCTA
    extra = 0
    max_num = 1


class ServiceDeliverableInline(admin.TabularInline):
    model = ServiceDeliverable
    extra = 0


class ServiceProcessStepInline(admin.TabularInline):
    model = ServiceProcessStep
    extra = 0


class ServiceFAQInline(admin.StackedInline):
    model = ServiceFAQ
    extra = 0


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "category", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ServiceKeyPointInline, ServiceDeliverableInline, ServiceFeatureInline, ServiceProcessStepInline, ServiceCTAInline, ServiceFAQInline]
    fieldsets = (
        ("Basic", {"fields": ("title", "slug", "category", "icon_text", "short_description")}),
        ("Content", {"fields": ("body",)}),
        ("Media", {"fields": ("cover_image", "brochure"), "description": "Service card thumbnail uses Cover image. Recommended upload size: 1200×650px or any clean 16:9 image. SVG, JPG, PNG or WebP are fine."}),
        ("Display", {"fields": ("is_featured", "sort_order", "is_active")}),
        ("SEO", {"fields": ("seo_title", "seo_description")}),
    )


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(ServiceListPageSettings)
class ServiceListPageSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Hero", {"fields": ("eyebrow", "hero_title", "hero_subtitle", "hero_image")}),
        ("Intro", {"fields": ("intro_title", "intro_text")}),
        ("Visibility", {"fields": ("show_search", "show_category_tabs", "show_featured_service", "show_process", "show_faqs")}),
    )


@admin.register(ServiceDetailPageSettings)
class ServiceDetailPageSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    list_display = ("default_hero_eyebrow", "show_key_points", "show_deliverables", "show_features", "show_process", "show_related_projects", "show_brochure", "show_faqs")


@admin.register(ServiceListProcessStep)
class ServiceListProcessStepAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "description")


@admin.register(ServiceListFAQ)
class ServiceListFAQAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("question", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("question",)


@admin.register(ServiceKeyPoint)
class ServiceKeyPointAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "service", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("service", "is_active")


@admin.register(ServiceFeature)
class ServiceFeatureAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "service", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("service", "is_active")


@admin.register(ServiceDeliverable)
class ServiceDeliverableAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "service", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("service", "is_active")
    search_fields = ("title", "description", "service__title")


@admin.register(ServiceProcessStep)
class ServiceProcessStepAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("step_number", "title", "service", "sort_order", "is_active")
    list_display_links = ("title",)
    list_editable = ("step_number", "sort_order", "is_active")
    list_filter = ("service", "is_active")
    search_fields = ("title", "description", "service__title")


@admin.register(ServiceFAQ)
class ServiceFAQAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("question", "service", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("service", "is_active")
    search_fields = ("question", "answer", "service__title")


@admin.register(ServiceCTA)
class ServiceCTAAdmin(admin.ModelAdmin):
    list_display = ("title", "service", "button_text", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "button_text", "service__title")
