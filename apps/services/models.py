from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field
from apps.core.models import OrderedActiveModel, TimeStampedModel


class ServiceCategory(OrderedActiveModel, TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    icon_text = models.CharField(max_length=40, blank=True)

    class Meta(OrderedActiveModel.Meta):
        verbose_name_plural = "Service categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Service(OrderedActiveModel, TimeStampedModel):
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, related_name="services", blank=True, null=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    icon_text = models.CharField(max_length=40, blank=True, default="⚙")
    short_description = models.TextField(blank=True)
    body = CKEditor5Field(blank=True, config_name="extends")
    cover_image = models.ImageField(upload_to="services/", blank=True, null=True)
    brochure = models.FileField(upload_to="services/brochures/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("service_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ServiceDeliverable(OrderedActiveModel, TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="deliverables")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title


class ServiceProcessStep(OrderedActiveModel, TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="process_steps")
    step_number = models.PositiveIntegerField(default=1)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    class Meta(OrderedActiveModel.Meta):
        ordering = ["step_number", "sort_order", "id"]

    def __str__(self):
        return f"{self.step_number}. {self.title}"


class ServiceFAQ(OrderedActiveModel, TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = CKEditor5Field(blank=True, config_name="extends")

    def __str__(self):
        return self.question


class ServiceListPageSettings(TimeStampedModel):
    hero_title = models.CharField(max_length=255, default="Integrated Engineering Solutions. Built on Expertise.")
    hero_subtitle = models.TextField(blank=True, default="End-to-end engineering services that power safe, efficient and sustainable buildings and infrastructure.")
    hero_image = models.ImageField(upload_to="services/list-page/", blank=True, null=True)
    eyebrow = models.CharField(max_length=120, default="Services Overview")
    intro_title = models.CharField(max_length=255, default="Services designed for reliable delivery.")
    intro_text = CKEditor5Field(blank=True, config_name="extends")
    show_search = models.BooleanField(default=True)
    show_category_tabs = models.BooleanField(default=True)
    show_featured_service = models.BooleanField(default=True)
    show_process = models.BooleanField(default=True)
    show_faqs = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service List Page Settings"
        verbose_name_plural = "Service List Page Settings"

    def __str__(self):
        return "Service List Page Settings"


class ServiceListProcessStep(OrderedActiveModel, TimeStampedModel):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title


class ServiceListFAQ(OrderedActiveModel, TimeStampedModel):
    question = models.CharField(max_length=255)
    answer = CKEditor5Field(blank=True, config_name="extends")

    def __str__(self):
        return self.question


class ServiceKeyPoint(OrderedActiveModel, TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="key_points")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title


class ServiceFeature(OrderedActiveModel, TimeStampedModel):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="features")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    icon_text = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.title


class ServiceCTA(TimeStampedModel):
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name="cta")
    title = models.CharField(max_length=255, default="Have a Project in Mind?")
    subtitle = models.TextField(blank=True)
    button_text = models.CharField(max_length=80, default="Get in Touch")
    button_url = models.CharField(max_length=255, default="/contact/")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"CTA for {self.service}"


class ServiceDetailPageSettings(TimeStampedModel):
    default_hero_eyebrow = models.CharField(max_length=120, default="Service Detail")
    show_key_points = models.BooleanField(default=True)
    show_deliverables = models.BooleanField(default=True)
    show_features = models.BooleanField(default=True)
    show_process = models.BooleanField(default=True)
    show_related_projects = models.BooleanField(default=True)
    show_brochure = models.BooleanField(default=True)
    show_faqs = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service Detail Page Settings"
        verbose_name_plural = "Service Detail Page Settings"

    def __str__(self):
        return "Service Detail Page Settings"
