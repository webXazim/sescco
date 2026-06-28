from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from apps.core.models import OrderedActiveModel, TimeStampedModel


class SEOFields(models.Model):
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)

    class Meta:
        abstract = True


class Page(TimeStampedModel, SEOFields):
    TEMPLATE_CHOICES = [
        ("home", "Home"),
        ("about", "About"),
        ("generic", "Generic"),
    ]
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_CHOICES, default="generic")
    hero_title = models.CharField(max_length=255, blank=True)
    hero_subtitle = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="pages/heroes/", blank=True, null=True)
    body = CKEditor5Field(blank=True, config_name="extends")
    is_published = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class PageSection(OrderedActiveModel, TimeStampedModel):
    SECTION_TYPES = [
        ("hero", "Hero"),
        ("text_image", "Text With Image"),
        ("stats", "Stats Row"),
        ("services_grid", "Services Grid"),
        ("projects_grid", "Projects Grid"),
        ("clients_strip", "Clients Strip"),
        ("certificates_grid", "Certificates Grid"),
        ("timeline", "Timeline"),
        ("faq", "FAQ"),
        ("cta", "CTA"),
        ("downloads", "Downloads"),
        ("gallery", "Gallery"),
        ("contact", "Contact Block"),
    ]
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="sections")
    section_type = models.CharField(max_length=50, choices=SECTION_TYPES)
    title = models.CharField(max_length=255, blank=True)
    subtitle = models.TextField(blank=True)
    content = CKEditor5Field(blank=True, config_name="extends")
    image = models.ImageField(upload_to="pages/sections/", blank=True, null=True)
    button_text = models.CharField(max_length=120, blank=True)
    button_url = models.CharField(max_length=255, blank=True)
    background_style = models.CharField(max_length=80, blank=True, default="white")
    layout_style = models.CharField(max_length=80, blank=True, default="standard")

    def __str__(self):
        return f"{self.page} - {self.title or self.section_type}"


class StatItem(OrderedActiveModel, TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="stats", blank=True, null=True)
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f"{self.value} {self.label}"


class TimelineItem(OrderedActiveModel, TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="timeline_items", blank=True, null=True)
    year = models.CharField(max_length=20)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.year} - {self.title}"


class FAQ(OrderedActiveModel, TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="faqs", blank=True, null=True)
    question = models.CharField(max_length=255)
    answer = CKEditor5Field(blank=True, config_name="extends")

    def __str__(self):
        return self.question


class HomeHero(TimeStampedModel):
    title = models.CharField(max_length=255, default="Where High-Quality Engineering Meets Reliable Service.")
    subtitle = models.TextField(blank=True)
    background_image = models.ImageField(upload_to="home/hero/", blank=True, null=True)
    primary_button_text = models.CharField(max_length=80, default="Our Services")
    primary_button_url = models.CharField(max_length=255, default="/services/")
    secondary_button_text = models.CharField(max_length=80, default="View Our Projects")
    secondary_button_url = models.CharField(max_length=255, default="/projects/")
    show_sphere = models.BooleanField(
        default=True,
        help_text="Turn the animated/service-card sphere on or off in the home page hero.",
    )
    sphere_auto_speed = models.FloatField(
        default=0.24,
        help_text="Base automatic sphere rotation speed. Higher is faster. Current production default: 0.24.",
    )
    sphere_scroll_speed = models.FloatField(
        default=0.03,
        help_text="Mouse wheel/manual rotation sensitivity. Higher lets users rotate the sphere faster. Current production default: 0.03.",
    )
    sphere_settle_seconds = models.FloatField(
        default=10.0,
        help_text="Approximate seconds for the sphere to settle back to the clean default X angle after manual rotation.",
    )
    sphere_max_boost = models.FloatField(
        default=0.55,
        help_text="Maximum temporary auto-rotation speed boost after fast manual scrolling. Higher feels more energetic.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Home Hero"
        verbose_name_plural = "Home Hero"

    def __str__(self):
        return self.title




class HomeHeroSphereCard(OrderedActiveModel, TimeStampedModel):
    CARD_TYPE_CHOICES = [
        ("image", "Image card"),
        ("data", "Data / text card"),
    ]

    title = models.CharField(max_length=120, help_text="Main label shown on image cards and used for accessibility.")
    subtitle = models.CharField(max_length=180, blank=True, help_text="Short supporting text shown on the card.")
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default="image")
    big_text = models.CharField(max_length=40, blank=True, help_text="Large text for data cards, such as QA, KSA, 2015, SEC.")
    image = models.ImageField(
        upload_to="home/sphere-cards/",
        blank=True,
        null=True,
        help_text="Upload card image for image cards. Recommended ratio: 3:4, at least 600 x 800 px. PNG/WebP/JPG.",
    )
    static_image_path = models.CharField(
        max_length=255,
        blank=True,
        help_text='Optional fallback static path, for example: "img/hero_sphere/project-01.svg". Uploaded image takes priority.',
    )
    alt_text = models.CharField(max_length=160, blank=True)
    is_featured = models.BooleanField(
        default=True,
        help_text="Featured cards are loaded into the home hero sphere. Keep 12–18 active cards for best shape.",
    )

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Home Hero Sphere Card"
        verbose_name_plural = "Home Hero Sphere Cards"

    def __str__(self):
        return f"{self.big_text or self.title}"


class HomeAboutBlock(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default="About")
    title = models.CharField(max_length=255, default="Engineering Solutions. Built on Trust.")
    body = CKEditor5Field(blank=True, config_name="extends")
    image = models.ImageField(upload_to="home/about/", blank=True, null=True)
    button_text = models.CharField(max_length=80, default="Learn More About Us")
    button_url = models.CharField(max_length=255, default="/about/")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Home About Block"
        verbose_name_plural = "Home About Block"

    def __str__(self):
        return self.title


class HomeSectionSettings(TimeStampedModel):
    services_eyebrow = models.CharField(max_length=120, default="Our Services")
    services_title = models.CharField(max_length=255, default="Integrated services under one roof.")
    services_limit = models.PositiveIntegerField(default=6)

    projects_eyebrow = models.CharField(max_length=120, default="Featured Projects")
    projects_title = models.CharField(max_length=255, default="Proof through delivered work.")
    projects_limit = models.PositiveIntegerField(default=4)

    clients_eyebrow = models.CharField(max_length=120, default="Our Clients")
    clients_limit = models.PositiveIntegerField(default=6)

    certificates_eyebrow = models.CharField(max_length=120, default="Certifications & Compliance")
    certificates_limit = models.PositiveIntegerField(default=6)

    why_choose_eyebrow = models.CharField(max_length=120, default="Why Choose Us?")
    why_choose_title = models.CharField(max_length=255, default="Why companies trust our delivery.")
    show_services = models.BooleanField(default=True)
    show_projects = models.BooleanField(default=True)
    show_clients = models.BooleanField(default=True)
    show_certificates = models.BooleanField(default=True)
    show_why_choose = models.BooleanField(default=True)
    show_custom_sections = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Home Section Settings"
        verbose_name_plural = "Home Section Settings"

    def __str__(self):
        return "Home Section Settings"


class WhyChooseItem(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_image = models.ImageField(
        upload_to="home/why-icons/",
        blank=True,
        null=True,
        help_text=(
            "Optional square icon image. Recommended upload size: 96 x 96 px "
            "PNG/WebP/JPG. It renders as 32 x 32 px inside a 58 x 58 px badge."
        ),
    )
    icon_text = models.CharField(
        max_length=40,
        blank=True,
        help_text="Fallback icon when no image is uploaded. Use one clean icon character such as ✓, ⚙, □, ✦, or an emoji. HTML is not required.",
    )
    show_on_home = models.BooleanField(default=True)
    show_on_about = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class HomeHighlight(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    value = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    icon_image = models.ImageField(
        upload_to="home/highlight-icons/",
        blank=True,
        null=True,
        help_text=(
            "Optional square icon image. Recommended upload size: 96 x 96 px "
            "PNG/WebP/JPG. It renders as 42 x 42 px inside a 72 x 72 px badge."
        ),
    )
    icon_text = models.CharField(
        max_length=40,
        blank=True,
        help_text="Fallback icon when no image is uploaded. Use one clean icon character such as ✓, ⚙, □, ✦, or an emoji. HTML is not required.",
    )
    link_text = models.CharField(max_length=80, blank=True)
    link_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title


class ValueItem(OrderedActiveModel, TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="value_items", blank=True, null=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title


class MissionVisionItem(OrderedActiveModel, TimeStampedModel):
    ITEM_TYPES = [
        ("mission", "Mission"),
        ("vision", "Vision"),
        ("values", "Values"),
        ("goal", "Goal"),
        ("purpose", "Purpose"),
    ]
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="mission_vision_items", blank=True, null=True)
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES, default="mission")
    title = models.CharField(max_length=120)
    description = CKEditor5Field(blank=True, config_name="extends")
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title


class LeadershipMessage(TimeStampedModel):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="leadership_messages", blank=True, null=True)
    title = models.CharField(max_length=255, default="Message from Leadership")
    message = CKEditor5Field(blank=True, config_name="extends")
    person_name = models.CharField(max_length=120, blank=True, default="Management Team")
    person_designation = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to="leadership/", blank=True, null=True)
    background_image = models.ImageField(upload_to="leadership/backgrounds/", blank=True, null=True, help_text="Optional full-width parallax background image for homepage leadership message section. Recommended 1920x900px or larger.")
    signature_image = models.ImageField(upload_to="leadership/signatures/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.title


class AboutPageSettings(TimeStampedModel):
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name="about_settings", blank=True, null=True)
    overview_eyebrow = models.CharField(max_length=120, default="Company Overview")
    overview_title = models.CharField(max_length=255, default="Engineering Solutions. Built on Trust.")
    overview_image = models.ImageField(upload_to="about/overview/", blank=True, null=True)
    mission_section_title = models.CharField(max_length=255, default="Mission, Vision & Values")
    timeline_eyebrow = models.CharField(max_length=120, default="Our Journey & Key Milestones")
    strengths_eyebrow = models.CharField(max_length=120, default="Our Strengths")
    strengths_title = models.CharField(max_length=255, default="Integrated expertise and proven delivery.")
    show_trust_strip = models.BooleanField(default=True)
    show_overview = models.BooleanField(default=True)
    show_mission_vision = models.BooleanField(default=True)
    show_timeline = models.BooleanField(default=True)
    show_strengths = models.BooleanField(default=True)
    show_leadership = models.BooleanField(default=True)
    show_stats = models.BooleanField(default=True)
    show_faqs = models.BooleanField(default=True)
    show_custom_sections = models.BooleanField(default=True)

    class Meta:
        verbose_name = "About Page Settings"
        verbose_name_plural = "About Page Settings"

    def __str__(self):
        return "About Page Settings"


class GenericPageSettings(TimeStampedModel):
    page = models.OneToOneField(Page, on_delete=models.CASCADE, related_name="generic_settings")
    show_breadcrumbs = models.BooleanField(default=True)
    show_cta = models.BooleanField(default=True)
    content_width = models.CharField(max_length=40, default="standard", choices=[("standard", "Standard"), ("narrow", "Narrow"), ("wide", "Wide")])
    sidebar_enabled = models.BooleanField(default=False)
    sidebar_title = models.CharField(max_length=120, blank=True)
    sidebar_content = CKEditor5Field(blank=True, config_name="extends")

    class Meta:
        verbose_name = "Generic Page Settings"
        verbose_name_plural = "Generic Page Settings"

    def __str__(self):
        return f"Settings for {self.page}"
class PageSectionOrder(TimeStampedModel):
    page_key = models.CharField(max_length=80, db_index=True, help_text="Internal page key, for example: home, about, services_list, project_detail.")
    page_label = models.CharField(max_length=160, blank=True)
    section_key = models.SlugField(max_length=120, help_text="Internal section key used by templates.")
    section_label = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=1, help_text="Priority number. 1 shows first, 2 shows second, 3 shows third. Keep it simple: use 1, 2, 3, 4, 5.")
    is_active = models.BooleanField(default=True, help_text="Disable to hide this section everywhere this page template uses it.")

    class Meta:
        ordering = ["page_key", "sort_order", "id"]
        unique_together = (("page_key", "section_key"),)
        verbose_name = "Page section order"
        verbose_name_plural = "Page section order"

    def __str__(self):
        return f"{self.page_label or self.page_key} — {self.section_label}"



class HomeSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Home section order"
        verbose_name_plural = "Home section order"


class AboutSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "About section order"
        verbose_name_plural = "About section order"


class ServicesListSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Services list section order"
        verbose_name_plural = "Services list section order"


class ServiceDetailSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Service detail section order"
        verbose_name_plural = "Service detail section order"


class ProjectsListSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Projects list section order"
        verbose_name_plural = "Projects list section order"


class ProjectDetailSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Project detail section order"
        verbose_name_plural = "Project detail section order"


class ClientsCertificationsSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Certifications & clients section order"
        verbose_name_plural = "Certifications & clients section order"


class CareersSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Careers section order"
        verbose_name_plural = "Careers section order"


class ContactSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Contact section order"
        verbose_name_plural = "Contact section order"


class DownloadsSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Downloads section order"
        verbose_name_plural = "Downloads section order"


class GenericSectionOrder(PageSectionOrder):
    class Meta:
        proxy = True
        verbose_name = "Generic page section order"
        verbose_name_plural = "Generic page section order"
