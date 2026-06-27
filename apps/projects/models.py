from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from apps.core.models import OrderedActiveModel, TimeStampedModel


class ProjectCategory(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    icon_text = models.CharField(max_length=40, blank=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name_plural = "Project categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Project(OrderedActiveModel, TimeStampedModel):
    STATUS_CHOICES = [("completed", "Completed"), ("ongoing", "Ongoing"), ("planned", "Planned")]
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, related_name="projects", blank=True, null=True)
    services = models.ManyToManyField("services.Service", related_name="projects", blank=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    client = models.ForeignKey("clients.Client", on_delete=models.SET_NULL, related_name="project_client_entries", blank=True, null=True)
    contractor = models.ForeignKey("clients.Client", on_delete=models.SET_NULL, related_name="project_contractor_entries", blank=True, null=True)
    client_name = models.CharField(max_length=255, blank=True)
    contractor_name = models.CharField(max_length=255, blank=True)
    client_logo = models.ImageField(upload_to="projects/stakeholders/", blank=True, null=True)
    contractor_logo = models.ImageField(upload_to="projects/stakeholders/", blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="completed")
    year = models.PositiveIntegerField(blank=True, null=True)
    duration = models.CharField(max_length=120, blank=True)
    short_description = models.TextField(blank=True)
    summary = CKEditor5Field(blank=True, config_name="extends")
    challenge = CKEditor5Field(blank=True, config_name="extends")
    scope = CKEditor5Field(blank=True, config_name="extends")
    solution = CKEditor5Field(blank=True, config_name="extends")
    outcomes = CKEditor5Field(blank=True, config_name="extends")
    cover_image = models.ImageField(upload_to="projects/", blank=True, null=True)
    project_profile = models.FileField(upload_to="projects/documents/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if self.client:
            self.client_name = self.client.name
            if self.client.logo:
                self.client_logo = self.client.logo

        if self.contractor:
            self.contractor_name = self.contractor.name
            if self.contractor.logo:
                self.contractor_logo = self.contractor.logo

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ProjectMetric(OrderedActiveModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="metrics")
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f"{self.value} {self.label}"


class ProjectImage(OrderedActiveModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="gallery")
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.caption or f"Image for {self.project}"


class ProjectListPageSettings(TimeStampedModel):
    eyebrow = models.CharField(max_length=120, default="Projects Overview")
    hero_title = models.CharField(max_length=255, default="Projects Delivered with Quality, Safety and Reliability.")
    hero_subtitle = models.TextField(blank=True, default="Explore successfully delivered projects spanning telecommunications, civil, electrical and architectural solutions.")
    hero_image = models.ImageField(upload_to="projects/list-page/", blank=True, null=True)
    intro_title = models.CharField(max_length=255, default="Proof through delivered work.")
    intro_text = CKEditor5Field(blank=True, config_name="extends")
    show_stats = models.BooleanField(default=True)
    show_category_tabs = models.BooleanField(default=True)
    show_search = models.BooleanField(default=True)
    show_featured_project = models.BooleanField(default=True)
    show_client_strip = models.BooleanField(default=True)
    show_cta = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Project List Page Settings"
        verbose_name_plural = "Project List Page Settings"

    def __str__(self):
        return "Project List Page Settings"


class ProjectDetailPageSettings(TimeStampedModel):
    default_hero_eyebrow = models.CharField(max_length=120, default="Project Case Study")
    show_summary = models.BooleanField(default=True)
    show_quick_facts = models.BooleanField(default=True)
    show_gallery = models.BooleanField(default=True)
    show_case_study_blocks = models.BooleanField(default=True)
    show_metrics = models.BooleanField(default=True)
    show_documents = models.BooleanField(default=True)
    show_related_projects = models.BooleanField(default=True)
    show_cta = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Project Detail Page Settings"
        verbose_name_plural = "Project Detail Page Settings"

    def __str__(self):
        return "Project Detail Page Settings"


class ProjectListStat(OrderedActiveModel, TimeStampedModel):
    label = models.CharField(max_length=120)
    value = models.CharField(max_length=120)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return f"{self.value} {self.label}"


class ProjectScopeItem(OrderedActiveModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="scope_items")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title


class ProjectDocument(OrderedActiveModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="projects/files/")
    description = models.TextField(blank=True)
    file_type = models.CharField(max_length=40, blank=True, default="PDF")

    def __str__(self):
        return self.title


class ProjectCTA(TimeStampedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="cta")
    title = models.CharField(max_length=255, default="Interested in a similar project?")
    subtitle = models.TextField(blank=True, default="Talk to our team about your project requirements.")
    button_text = models.CharField(max_length=80, default="Start a Project")
    button_url = models.CharField(max_length=255, default="/contact/")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"CTA for {self.project}"
