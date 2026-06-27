from django.contrib import admin
from apps.core.admin_safety import ProductionAdminSafetyMixin, SingletonAdminSafetyMixin
from django.utils.html import format_html
from .models import Project, ProjectCTA, ProjectCategory, ProjectDetailPageSettings, ProjectDocument, ProjectImage, ProjectListPageSettings, ProjectListStat, ProjectMetric, ProjectScopeItem




class ProjectScopeItemInline(admin.TabularInline):
    model = ProjectScopeItem
    extra = 0


class ProjectDocumentInline(admin.TabularInline):
    model = ProjectDocument
    extra = 0


class ProjectCTAInline(admin.StackedInline):
    model = ProjectCTA
    extra = 0
    max_num = 1


class ProjectMetricInline(admin.TabularInline):
    model = ProjectMetric
    extra = 0


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ("image_preview", "image", "caption", "sort_order", "is_active")
    readonly_fields = ("image_preview",)

    @admin.display(description="Preview")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:96px;height:64px;object-fit:cover;border-radius:10px;border:1px solid #dbe7fb;background:#fff;" alt="" />', obj.image.url)
        return "Upload image"


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "category", "client", "contractor", "status", "year", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("category", "status", "client", "contractor", "is_featured", "is_active")
    search_fields = ("title", "client_name", "contractor_name", "client__name", "contractor__name", "location", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("services",)
    autocomplete_fields = ("client", "contractor")
    inlines = [ProjectMetricInline, ProjectScopeItemInline, ProjectImageInline, ProjectDocumentInline, ProjectCTAInline]
    fieldsets = (
        ("Basic", {"fields": ("title", "slug", "category", "services", "short_description")}),
        ("Stakeholders", {"fields": ("client", "contractor", "client_name", "client_logo", "contractor_name", "contractor_logo"), "description": "Select the client and contractor companies here to automatically reuse their names and logos on the public project page. Manual fields remain available as fallback overrides."}),
        ("Project Details", {"fields": ("location", "status", "year", "duration")}),
        ("Project Description (CKEditor 5)", {"fields": ("summary",), "description": "Use this as the single rich project description input shown on the public project detail page."}),
        ("Media", {"fields": ("cover_image", "project_profile")}),
        ("Display", {"fields": ("is_featured", "sort_order", "is_active")}),
        ("SEO", {"fields": ("seo_title", "seo_description")}),
    )


class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(ProjectListPageSettings)
class ProjectListPageSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Hero", {"fields": ("eyebrow", "hero_title", "hero_subtitle", "hero_image")}),
        ("Intro", {"fields": ("intro_title", "intro_text")}),
        ("Visibility", {"fields": ("show_stats", "show_category_tabs", "show_search", "show_featured_project", "show_client_strip", "show_cta")}),
    )


@admin.register(ProjectDetailPageSettings)
class ProjectDetailPageSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    list_display = ("default_hero_eyebrow", "show_summary", "show_quick_facts", "show_gallery", "show_case_study_blocks", "show_metrics", "show_documents", "show_related_projects", "show_cta")


@admin.register(ProjectListStat)
class ProjectListStatAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("label", "value", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("label", "value")


@admin.register(ProjectScopeItem)
class ProjectScopeItemAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "project", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("project", "is_active")


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "project", "file_type", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("project", "file_type", "is_active")


@admin.register(ProjectMetric)
class ProjectMetricAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("label", "value", "project", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("project", "is_active")
    search_fields = ("label", "value", "project__title")


@admin.register(ProjectImage)
class ProjectImageAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("admin_preview", "project", "caption", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("project", "is_active")
    search_fields = ("caption", "project__title")
    readonly_fields = ("admin_preview",)

    @admin.display(description="Preview")
    def admin_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="width:96px;height:64px;object-fit:cover;border-radius:10px;border:1px solid #dbe7fb;background:#fff;" alt="" />', obj.image.url)
        return "—"


@admin.register(ProjectCTA)
class ProjectCTAAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "button_text", "is_active")
    list_editable = ("is_active",)
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "button_text", "project__title")
