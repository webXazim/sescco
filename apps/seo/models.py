from django.db import models


class RedirectRule(models.Model):
    old_path = models.CharField(max_length=255, unique=True, help_text="Example: /old-page/")
    new_path = models.CharField(max_length=255, help_text="Example: /new-page/")
    is_active = models.BooleanField(default=True)
    permanent = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.old_path} → {self.new_path}"


class RobotsSettings(models.Model):
    content = models.TextField(default="User-agent: *\nAllow: /\nSitemap: /sitemap.xml")

    class Meta:
        verbose_name = "Robots.txt Settings"
        verbose_name_plural = "Robots.txt Settings"

    def __str__(self):
        return "Robots.txt Settings"


class SchemaMarkup(models.Model):
    title = models.CharField(max_length=120)
    page_path = models.CharField(max_length=255, blank=True, help_text="Example: /about/. Leave blank for global.")
    json_ld = models.TextField(help_text="Paste valid JSON-LD.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
