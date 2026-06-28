import json
from urllib.parse import urlencode

from django.contrib import admin
from apps.core.admin_safety import ProductionAdminSafetyMixin, SingletonAdminSafetyMixin
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponseBadRequest, JsonResponse
from django.urls import NoReverseMatch, path, reverse
from django.utils.html import format_html
from django.apps import apps as django_apps
from .models import AboutPageSettings, FAQ, GenericPageSettings, HomeAboutBlock, HomeHero, HomeHeroSphereCard, HomeHighlight, HomeSectionSettings, LeadershipMessage, MissionVisionItem, Page, PageSection, PageSectionOrder, StatItem, TimelineItem, ValueItem, WhyChooseItem, HomeSectionOrder, AboutSectionOrder, ServicesListSectionOrder, ServiceDetailSectionOrder, ProjectsListSectionOrder, ProjectDetailSectionOrder, ClientsCertificationsSectionOrder, CareersSectionOrder, ContactSectionOrder, GenericSectionOrder




class MissionVisionItemInline(admin.StackedInline):
    model = MissionVisionItem
    extra = 0


class ValueItemInline(admin.TabularInline):
    model = ValueItem
    extra = 0


class LeadershipMessageInline(admin.StackedInline):
    model = LeadershipMessage
    extra = 0


class AboutPageSettingsInline(admin.StackedInline):
    model = AboutPageSettings
    extra = 0
    max_num = 1


class GenericPageSettingsInline(admin.StackedInline):
    model = GenericPageSettings
    extra = 0
    max_num = 1


class PageSectionInline(admin.StackedInline):
    model = PageSection
    extra = 0


class StatItemInline(admin.TabularInline):
    model = StatItem
    extra = 0


class TimelineItemInline(admin.TabularInline):
    model = TimelineItem
    extra = 0


class FAQInline(admin.StackedInline):
    model = FAQ
    extra = 0


@admin.register(Page)
class PageAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("title", "slug", "template_type", "is_published", "updated_at")
    list_filter = ("template_type", "is_published")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [AboutPageSettingsInline, GenericPageSettingsInline, PageSectionInline, MissionVisionItemInline, ValueItemInline, StatItemInline, TimelineItemInline, LeadershipMessageInline, FAQInline]
    fieldsets = (
        ("Basic", {"fields": ("title", "slug", "template_type", "is_published")}),
        ("Hero", {"fields": ("hero_title", "hero_subtitle", "hero_image")}),
        ("Body", {"fields": ("body",)}),
        ("SEO", {"fields": ("seo_title", "seo_description", "og_image")}),
    )


@admin.register(PageSection)
class PageSectionAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("page", "section_type", "title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("page", "section_type", "is_active")
    search_fields = ("page__title", "page__slug", "title", "subtitle", "content")


@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "page", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("page", "is_active")
    search_fields = ("label", "value")


@admin.register(TimelineItem)
class TimelineItemAdmin(admin.ModelAdmin):
    list_display = ("year", "title", "page", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("page", "is_active")
    search_fields = ("year", "title", "description")


@admin.register(FAQ)
class FAQAdmin(ProductionAdminSafetyMixin, admin.ModelAdmin):
    list_display = ("question", "page", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("page", "is_active")
    search_fields = ("question", "answer")




class SingletonAdminMixin:
    def has_add_permission(self, request):
        return not self.model.objects.exists()


@admin.register(HomeHero)
class HomeHeroAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Hero Content", {"fields": ("title", "subtitle", "background_image", "show_sphere", "is_active"), "description": "Homepage visual image: upload/update the engineers photo shown on the right side of the hero section. Use Show sphere to turn the animated service-card sphere on or off."}),
        ("Sphere Motion", {"fields": ("sphere_auto_speed", "sphere_scroll_speed", "sphere_settle_seconds", "sphere_max_boost"), "description": "Tune the home hero sphere without code changes. Increase slowly; small decimal changes are visible."}),
        ("Primary Button", {"fields": ("primary_button_text", "primary_button_url")}),
        ("Secondary Button", {"fields": ("secondary_button_text", "secondary_button_url")}),
    )





@admin.register(HomeHeroSphereCard)
class HomeHeroSphereCardAdmin(admin.ModelAdmin):
    list_display = ("preview", "title", "card_type", "big_text", "is_featured", "sort_order", "is_active")
    list_editable = ("is_featured", "sort_order", "is_active")
    list_filter = ("card_type", "is_featured", "is_active")
    search_fields = ("title", "subtitle", "big_text", "alt_text", "static_image_path")
    readonly_fields = ("preview",)
    fieldsets = (
        (
            "Card Content",
            {
                "fields": ("preview", "card_type", "title", "subtitle", "big_text"),
                "description": (
                    "Use Image card for project/visual cards, or Data card for text-based proof cards such as QA, KSA, SEC, 2015."
                ),
            },
        ),
        (
            "Image",
            {
                "fields": ("image", "static_image_path", "alt_text"),
                "description": (
                    "Uploaded image takes priority. Static fallback path is optional and mainly used by seeded default cards."
                ),
            },
        ),
        ("Sphere Display", {"fields": ("is_featured", "sort_order", "is_active")}),
    )

    @admin.display(description="Preview")
    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" alt="" style="width:44px;height:58px;object-fit:cover;border-radius:12px;box-shadow:0 8px 18px rgba(0,0,0,.14);" />',
                obj.image.url,
            )
        if obj and obj.static_image_path:
            return format_html(
                '<span style="display:inline-flex;width:44px;height:58px;align-items:center;justify-content:center;border-radius:12px;background:#eef6ff;color:#075ed8;font-weight:800;font-size:10px;text-align:center;">static</span>'
            )
        if obj and obj.big_text:
            return format_html(
                '<span style="display:inline-flex;width:44px;height:58px;align-items:center;justify-content:center;border-radius:12px;background:#eef6ff;color:#075ed8;font-weight:900;">{}</span>',
                obj.big_text,
            )
        return "—"


@admin.register(HomeAboutBlock)
class HomeAboutBlockAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Content", {"fields": ("eyebrow", "title", "body", "image", "is_active")}),
        ("Button", {"fields": ("button_text", "button_url")}),
    )


@admin.register(HomeSectionSettings)
class HomeSectionSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Services", {"fields": ("show_services", "services_eyebrow", "services_title", "services_limit")}),
        ("Projects", {"fields": ("show_projects", "projects_eyebrow", "projects_title", "projects_limit")}),
        ("Clients", {"fields": ("show_clients", "clients_eyebrow", "clients_limit")}),
        ("Certificates", {"fields": ("show_certificates", "certificates_eyebrow", "certificates_limit")}),
        ("Why Choose", {"fields": ("show_why_choose", "why_choose_eyebrow", "why_choose_title")}),
        ("Custom Sections", {"fields": ("show_custom_sections",)}),
    )


@admin.register(WhyChooseItem)
class WhyChooseItemAdmin(admin.ModelAdmin):
    list_display = ("icon_preview", "title", "show_on_home", "show_on_about", "sort_order", "is_active")
    list_editable = ("show_on_home", "show_on_about", "sort_order", "is_active")
    list_filter = ("show_on_home", "show_on_about", "is_active")
    search_fields = ("title", "description", "icon_text")
    readonly_fields = ("icon_preview",)
    fieldsets = (
        ("Content", {"fields": ("title", "description")}),
        (
            "Icon",
            {
                "fields": ("icon_preview", "icon_image", "icon_text"),
                "description": (
                    "Use either an uploaded square icon image or a text icon. "
                    "Uploaded image takes priority. Recommended upload: 96 x 96 px PNG/WebP/JPG; "
                    "front-end display: 32 x 32 px inside a 58 x 58 px badge."
                ),
            },
        ),
        ("Visibility / Ordering", {"fields": ("show_on_home", "show_on_about", "sort_order", "is_active")}),
    )

    @admin.display(description="Icon")
    def icon_preview(self, obj):
        if obj and obj.icon_image:
            return format_html(
                '<img src="{}" alt="" style="width:34px;height:34px;object-fit:contain;border-radius:8px;" />',
                obj.icon_image.url,
            )
        if obj and obj.icon_text:
            return obj.icon_text
        return "✓"


@admin.register(HomeHighlight)
class HomeHighlightAdmin(admin.ModelAdmin):
    list_display = ("icon_preview", "title", "value", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title", "value", "description", "icon_text")
    readonly_fields = ("icon_preview",)
    fieldsets = (
        ("Content", {"fields": ("title", "value", "description")}),
        (
            "Icon",
            {
                "fields": ("icon_preview", "icon_image", "icon_text"),
                "description": (
                    "Use either an uploaded square icon image or a text icon. "
                    "Uploaded image takes priority. Recommended upload: 96 x 96 px PNG/WebP/JPG; "
                    "front-end display: 42 x 42 px inside a 72 x 72 px badge."
                ),
            },
        ),
        ("Button", {"fields": ("link_text", "link_url")}),
        ("Ordering / Visibility", {"fields": ("sort_order", "is_active")}),
    )

    @admin.display(description="Icon")
    def icon_preview(self, obj):
        if obj and obj.icon_image:
            return format_html(
                '<img src="{}" alt="" style="width:34px;height:34px;object-fit:contain;border-radius:8px;" />',
                obj.icon_image.url,
            )
        if obj and obj.icon_text:
            return obj.icon_text
        return "✦"


@admin.register(AboutPageSettings)
class AboutPageSettingsAdmin(admin.ModelAdmin):
    list_display = ("page", "show_trust_strip", "show_overview", "show_mission_vision", "show_timeline", "show_strengths", "show_leadership")


@admin.register(GenericPageSettings)
class GenericPageSettingsAdmin(admin.ModelAdmin):
    list_display = ("page", "content_width", "sidebar_enabled", "show_breadcrumbs", "show_cta")


@admin.register(MissionVisionItem)
class MissionVisionItemAdmin(admin.ModelAdmin):
    list_display = ("title", "item_type", "page", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("page", "item_type", "is_active")
    search_fields = ("page__title", "title", "description")


@admin.register(ValueItem)
class ValueItemAdmin(admin.ModelAdmin):
    list_display = ("title", "page", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("page", "is_active")
    search_fields = ("page__title", "title", "description")


@admin.register(LeadershipMessage)
class LeadershipMessageAdmin(admin.ModelAdmin):
    list_display = ("title", "person_name", "person_designation", "page", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    list_filter = ("page", "is_active")
    search_fields = ("page__title", "title", "person_name", "person_designation", "message")
    fieldsets = (
        ("Placement", {"fields": ("page", "is_active", "sort_order")}),
        ("Message", {"fields": ("title", "message")}),
        ("Attribution", {"fields": ("person_name", "person_designation", "signature_image")}),
        ("Parallax Background", {"fields": ("background_image",), "description": "Upload a wide industrial/engineering background for the leadership message section on Home or About. Recommended: 1920x900px or larger, JPG/WebP."}),
        ("Legacy Portrait / Logo", {"fields": ("image",), "description": "Optional legacy image. The current parallax message design does not show a portrait."}),
    )



_PRIORITY_WORDS = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
}


def _priority_label(value):
    word = _PRIORITY_WORDS.get(value)
    if word:
        return f"{value} — show {word}"
    return f"{value}"




def _safe_reverse_admin(app_label, model_name, action="changelist", args=None, params=None):
    """Build admin URLs without breaking the section order screen if a model changes."""
    try:
        url = reverse(f"admin:{app_label}_{model_name}_{action}", args=args or [])
    except NoReverseMatch:
        return ""
    if params:
        clean_params = {key: value for key, value in params.items() if value not in (None, "")}
        query = urlencode(clean_params, doseq=True)
        if query:
            url = f"{url}?{query}"
    return url


def _model_admin_url(app_label, model_class_name, *, singleton=False, params=None):
    """Return the most useful admin editor for a model.

    For singleton/settings models, open the existing object change form when it
    exists, otherwise open the add form. For collection models, open the normal
    changelist where admins can add or edit multiple records.
    """
    try:
        model = django_apps.get_model(app_label, model_class_name)
    except LookupError:
        return ""
    model_name = model._meta.model_name
    if singleton:
        obj = model.objects.order_by("pk").first()
        if obj:
            return _safe_reverse_admin(app_label, model_name, "change", args=[obj.pk])
        return _safe_reverse_admin(app_label, model_name, "add")
    return _safe_reverse_admin(app_label, model_name, "changelist", params=params)




def _queryset_for_admin_params(model, params):
    """Best-effort queryset matching for admin query params.

    This lets a section-order row open the exact change form when the section
    is backed by a single record, while still opening a filtered changelist for
    collection sections such as FAQs, timeline items, service cards, or custom
    PageSection blocks.
    """
    qs = model.objects.all()
    filters = {}
    for key, value in (params or {}).items():
        if key == "q" or value in (None, ""):
            continue
        filters[key] = value
    if filters:
        try:
            qs = qs.filter(**filters)
        except Exception:
            return model.objects.none()
    return qs


def _filtered_model_admin_url(app_label, model_class_name, *, params=None, open_single=True):
    try:
        model = django_apps.get_model(app_label, model_class_name)
    except LookupError:
        return ""
    model_name = model._meta.model_name
    query_params = params or {}
    if open_single:
        qs = _queryset_for_admin_params(model, query_params)
        try:
            if qs.count() == 1:
                return _safe_reverse_admin(app_label, model_name, "change", args=[qs.first().pk])
        except Exception:
            pass
    return _safe_reverse_admin(app_label, model_name, "changelist", params=query_params)


def _page_scoped_params(template_type, extra=None):
    params = {}
    page = Page.objects.filter(template_type=template_type).order_by("pk").first()
    if page:
        params["page__id__exact"] = page.pk
    if extra:
        params.update(extra)
    return params


def _page_scoped_model_admin_url(app_label, model_class_name, template_type, *, extra=None, open_single=True):
    return _filtered_model_admin_url(
        app_label,
        model_class_name,
        params=_page_scoped_params(template_type, extra=extra),
        open_single=open_single,
    )

def _page_admin_url(template_type=None, slug=None):
    """Open the matching Page change form when possible; fall back to page list."""
    query = {}
    if slug:
        query["slug"] = slug
    if template_type:
        query["template_type"] = template_type

    qs = Page.objects.all()
    if slug:
        qs = qs.filter(slug=slug)
    if template_type:
        qs = qs.filter(template_type=template_type)
    page = qs.order_by("pk").first()
    if page:
        return _safe_reverse_admin("pages", "page", "change", args=[page.pk])
    return _safe_reverse_admin("pages", "page", "changelist", params={"q": slug or template_type or ""})


# Primary content editor for each frontend section. These links make the
# drag-and-drop ordering screen a practical content map too: click a section
# title to open the admin form/list where that section's real content is edited.
SECTION_CONTENT_EDITORS = {
    "home": {
        "hero": ("model", "pages", "HomeHero", True),
        "trust_strip": ("model", "core", "CompanyProfile", True),
        "highlights": ("filtered_model", "pages", "HomeHighlight", {"is_active__exact": "1"}, False),
        "leadership": ("filtered_model", "pages", "LeadershipMessage", {"is_active__exact": "1"}, False),
        "about": ("model", "pages", "HomeAboutBlock", True),
        "services": ("filtered_model", "services", "Service", {"is_featured__exact": "1"}, False),
        "projects": ("filtered_model", "projects", "Project", {"is_featured__exact": "1"}, False),
        "proof": ("model", "pages", "HomeSectionSettings", True),
        "why_choose": ("filtered_model", "pages", "WhyChooseItem", {"show_on_home__exact": "1"}, False),
        "custom_sections": ("page_model", "pages", "PageSection", "home", {}, True),
    },
    "about": {
        "hero": ("page", "about", None, None),
        "trust_strip": ("model", "core", "CompanyProfile", True),
        "overview": ("model", "pages", "AboutPageSettings", True),
        "mission_vision": ("page_model", "pages", "MissionVisionItem", "about", {}, False),
        "timeline": ("page_model", "pages", "TimelineItem", "about", {}, False),
        "strengths": ("filtered_model", "pages", "WhyChooseItem", {"show_on_about__exact": "1"}, False),
        "stats": ("page_model", "pages", "StatItem", "about", {}, False),
        "leadership": ("page_model", "pages", "LeadershipMessage", "about", {}, True),
        "custom_sections": ("page_model", "pages", "PageSection", "about", {}, True),
        "faqs": ("page_model", "pages", "FAQ", "about", {}, True),
    },
    "services_list": {
        "hero": ("model", "services", "ServiceListPageSettings", True),
        "search_services": ("model", "services", "Service", False),
        "featured_service": ("filtered_model", "services", "Service", {"is_featured__exact": "1"}, False),
        "process": ("model", "services", "ServiceListProcessStep", False),
        "faqs": ("model", "services", "ServiceListFAQ", False),
    },
    "service_detail": {
        "hero": ("model", "services", "Service", False),
        "key_points": ("model", "services", "ServiceKeyPoint", False),
        "body_summary": ("model", "services", "Service", False),
        "deliverables": ("model", "services", "ServiceDeliverable", False),
        "features": ("model", "services", "ServiceFeature", False),
        "process": ("model", "services", "ServiceProcessStep", False),
        "related_projects": ("model", "projects", "Project", False),
        "brochure": ("model", "services", "Service", False),
        "faqs": ("model", "services", "ServiceFAQ", False),
    },
    "projects_list": {
        "hero": ("model", "projects", "ProjectListPageSettings", True),
        "stats": ("model", "projects", "ProjectListStat", False),
        "portfolio": ("model", "projects", "Project", False),
        "client_strip": ("model", "clients", "Client", False),
        "cta": ("model", "projects", "ProjectListPageSettings", True),
    },
    "project_detail": {
        "hero": ("model", "projects", "Project", False),
        "gallery": ("model", "projects", "ProjectImage", False),
        "overview": ("model", "projects", "Project", False),
        "deliverables": ("model", "projects", "ProjectScopeItem", False),
        "case_study": ("model", "projects", "Project", False),
        "detailed_scope": ("model", "projects", "ProjectScopeItem", False),
        "metrics": ("model", "projects", "ProjectMetric", False),
        "documents_cta": ("model", "projects", "ProjectDocument", False),
        "related_projects": ("model", "projects", "Project", False),
    },
    "clients_certifications": {
        "hero": ("model", "clients", "TrustPageSettings", True),
        "metrics": ("model", "clients", "TrustMetric", False),
        "certificates": ("model", "clients", "Certificate", False),
        "clients": ("model", "clients", "Client", False),
        "accreditations": ("model", "clients", "Accreditation", False),
        "standards": ("model", "clients", "Standard", False),
        "testimonials": ("model", "clients", "Testimonial", False),
        "documents": ("model", "documents", "DownloadDocument", False),
    },
    "careers": {
        "hero": ("model", "careers", "CareerPageSettings", True),
        "stats": ("model", "careers", "CareerStat", False),
        "jobs": ("model", "careers", "JobOpening", False),
        "benefits": ("model", "careers", "CareerBenefit", False),
        "process": ("model", "careers", "CareerProcessStep", False),
        "cta": ("model", "careers", "CareerPageSettings", True),
    },
    "contact": {
        "hero": ("model", "inquiries", "ContactPageSettings", True),
        "intro_form": ("model", "inquiries", "ContactPageSettings", True),
        "offices": ("model", "core", "OfficeLocation", False),
        "map": ("model", "inquiries", "ContactPageSettings", True),
        "faqs": ("page_model", "pages", "FAQ", "generic", {"q": "contact"}, False),
    },
    "generic": {
        "hero": ("page", "generic", None, None),
        "body": ("page", "generic", None, None),
        "custom_sections": ("model", "pages", "PageSection", False),
        "faqs": ("model", "pages", "FAQ", False),
    },
}

def _section_content_url(page_key, section_key):
    editor = SECTION_CONTENT_EDITORS.get(page_key, {}).get(section_key)
    if not editor:
        return ""
    editor_type = editor[0]
    if editor_type == "page":
        template_type = editor[1]
        return _page_admin_url(template_type=template_type)
    if editor_type == "model":
        _, app_label, model_or_none, singleton = editor
        return _model_admin_url(app_label, model_or_none, singleton=bool(singleton))
    if editor_type == "filtered_model":
        _, app_label, model_or_none, params, open_single = editor
        return _filtered_model_admin_url(app_label, model_or_none, params=params, open_single=bool(open_single))
    if editor_type == "page_model":
        _, app_label, model_or_none, template_type, extra_params, open_single = editor
        return _page_scoped_model_admin_url(app_label, model_or_none, template_type, extra=extra_params, open_single=bool(open_single))
    return ""



class PageSpecificSectionOrderAdmin(admin.ModelAdmin):
    """Drag-and-drop page-by-page section priority editor.

    Admins edit one page template at a time. Drag rows into the desired
    sequence, then save. The first row renders first on the frontend, the
    second row renders second, and so on. Unchecking Active hides a section.
    """
    page_key = None
    page_label = "Page"
    change_list_template = "admin/pages/section_order_drag_changelist.html"
    list_display = ("drag_handle", "section_editor_link", "description_short", "content_editor_action", "active_toggle")
    list_display_links = None
    ordering = ("sort_order", "id")
    search_fields = ()
    list_filter = ()
    list_per_page = 200
    actions = None
    sortable_by = ()
    fields = ("section_label", "sort_order", "is_active", "description", "section_key", "page_label")
    readonly_fields = ("section_label", "section_key", "page_label", "description")

    @admin.display(description="Order")
    def drag_handle(self, obj):
        return format_html(
            '<span class="sescco-drag-cell">'
            '<span class="sescco-drag-handle" data-object-id="{}" title="Drag this section">↕</span>'
            '<span class="sescco-order-number">{}</span>'
            '</span>',
            obj.pk,
            obj.sort_order,
        )

    @admin.display(description="Section")
    def section_editor_link(self, obj):
        url = _section_content_url(obj.page_key, obj.section_key)
        if url:
            return format_html('<a href="{}">{}</a>', url, obj.section_label)
        return obj.section_label

    @admin.display(description="Edit content")
    def content_editor_action(self, obj):
        url = _section_content_url(obj.page_key, obj.section_key)
        if url:
            return format_html('<a class="button" href="{}">Open editor</a>', url)
        return format_html('<span class="quiet">No editor mapped</span>')

    @admin.display(description="Admin note")
    def description_short(self, obj):
        return obj.description

    @admin.display(description="Is active")
    def active_toggle(self, obj):
        checked = " checked" if obj.is_active else ""
        return format_html(
            '<input type="checkbox" class="sescco-section-active" data-object-id="{}"{} aria-label="Show {}">',
            obj.pk,
            checked,
            obj.section_label,
        )

    def get_queryset(self, request):
        from .section_registry import PAGE_SECTION_REGISTRY

        valid_section_keys = [item[0] for item in PAGE_SECTION_REGISTRY.get(self.page_key, {}).get("sections", [])]
        queryset = super().get_queryset(request).filter(page_key=self.page_key)
        if valid_section_keys:
            queryset = queryset.filter(section_key__in=valid_section_keys)
        return queryset.order_by("sort_order", "id")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "reorder/",
                self.admin_site.admin_view(self.reorder_view),
                name=f"{self.model._meta.app_label}_{self.model._meta.model_name}_reorder",
            ),
        ]
        return custom_urls + urls

    def reorder_view(self, request):
        if request.method != "POST":
            return HttpResponseBadRequest("POST required")
        if not self.has_change_permission(request):
            return JsonResponse({"ok": False, "error": "Permission denied"}, status=403)
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")

        raw_order = payload.get("order", [])
        active_map = payload.get("active", {})
        if not isinstance(raw_order, list) or not raw_order:
            return HttpResponseBadRequest("Missing order list")

        try:
            ordered_ids = [int(value) for value in raw_order]
        except (TypeError, ValueError):
            return HttpResponseBadRequest("Invalid order ids")

        qs = self.get_queryset(request).filter(pk__in=ordered_ids)
        objects_by_id = {obj.pk: obj for obj in qs}
        if len(objects_by_id) != len(set(ordered_ids)):
            return HttpResponseBadRequest("Some sections were not found for this page")

        changed = []
        with transaction.atomic():
            for index, object_id in enumerate(ordered_ids, start=1):
                obj = objects_by_id[object_id]
                obj.sort_order = index
                if str(object_id) in active_map:
                    obj.is_active = bool(active_map[str(object_id)])
                changed.append(obj)
            self.model.objects.bulk_update(changed, ["sort_order", "is_active"])

        cache.delete("cms_section_order_map")
        return JsonResponse({"ok": True, "updated": len(changed)})

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = f"{self.page_label} section order"
        extra_context["subtitle"] = "Drag and drop rows. Top row shows first, second row shows second."
        extra_context["section_order_reorder_url"] = "reorder/"
        extra_context["section_order_page_label"] = self.page_label
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_model_perms(self, request):
        # Show the simpler page-specific editors in the admin sidebar.
        return super().get_model_perms(request)


@admin.register(HomeSectionOrder)
class HomeSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "home"
    page_label = "Home page"


@admin.register(AboutSectionOrder)
class AboutSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "about"
    page_label = "About page"


@admin.register(ServicesListSectionOrder)
class ServicesListSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "services_list"
    page_label = "Services list page"


@admin.register(ServiceDetailSectionOrder)
class ServiceDetailSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "service_detail"
    page_label = "Service detail page"


@admin.register(ProjectsListSectionOrder)
class ProjectsListSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "projects_list"
    page_label = "Projects list page"


@admin.register(ProjectDetailSectionOrder)
class ProjectDetailSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "project_detail"
    page_label = "Project detail page"


@admin.register(ClientsCertificationsSectionOrder)
class ClientsCertificationsSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "clients_certifications"
    page_label = "Certifications & clients page"


@admin.register(CareersSectionOrder)
class CareersSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "careers"
    page_label = "Careers page"


@admin.register(ContactSectionOrder)
class ContactSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "contact"
    page_label = "Contact page"



@admin.register(GenericSectionOrder)
class GenericSectionOrderAdmin(PageSpecificSectionOrderAdmin):
    page_key = "generic"
    page_label = "Generic CMS page"

# Keep section ordering easy to find: move all page-specific section order
# proxy admins into their own admin group instead of mixing them into Pages.
_SECTION_ORDER_MODEL_OBJECTS = {
    "HomeSectionOrder",
    "AboutSectionOrder",
    "ServicesListSectionOrder",
    "ServiceDetailSectionOrder",
    "ProjectsListSectionOrder",
    "ProjectDetailSectionOrder",
    "ClientsCertificationsSectionOrder",
    "CareersSectionOrder",
    "ContactSectionOrder",
    "GenericSectionOrder",
}

if not getattr(admin.site, "_sescco_section_order_group_patched", False):
    _original_get_app_list = admin.site.get_app_list

    def _sescco_get_app_list(request, app_label=None):
        app_list = _original_get_app_list(request, app_label)
        if app_label is not None:
            return app_list

        section_order_models = []
        cleaned_app_list = []
        for app in app_list:
            remaining_models = []
            for model in app.get("models", []):
                if model.get("object_name") in _SECTION_ORDER_MODEL_OBJECTS:
                    section_order_models.append(model)
                else:
                    remaining_models.append(model)
            if remaining_models:
                app = app.copy()
                app["models"] = remaining_models
                cleaned_app_list.append(app)

        if section_order_models:
            section_order_rank = {
                "HomeSectionOrder": 1,
                "AboutSectionOrder": 2,
                "ServicesListSectionOrder": 3,
                "ServiceDetailSectionOrder": 4,
                "ProjectsListSectionOrder": 5,
                "ProjectDetailSectionOrder": 6,
                "ClientsCertificationsSectionOrder": 7,
                "CareersSectionOrder": 8,
                "ContactSectionOrder": 9,
                "GenericSectionOrder": 10,
            }
            section_order_models.sort(key=lambda model: section_order_rank.get(model.get("object_name"), 999))
            cleaned_app_list.insert(1, {
                "name": "Page section ordering",
                "app_label": "page_section_ordering",
                "app_url": "",
                "has_module_perms": True,
                "models": section_order_models,
            })
        return cleaned_app_list

    admin.site.get_app_list = _sescco_get_app_list
    admin.site._sescco_section_order_group_patched = True
