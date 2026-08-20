from io import BytesIO
from pathlib import PurePosixPath

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageOps, UnidentifiedImageError


# High-traffic public imagery only. Certificates and downloadable originals are
# intentionally excluded because small text must remain lossless.
IMAGE_FIELDS = (
    ("core", "CompanyProfile", "logo", (512, 512)),
    ("pages", "HomeHero", "background_image", (1920, 1200)),
    ("pages", "HomeHeroSphereCard", "image", (720, 960)),
    ("pages", "HomeAboutBlock", "image", (1280, 960)),
    ("pages", "LeadershipMessage", "image", (1000, 1000)),
    ("pages", "LeadershipMessage", "background_image", (1920, 1200)),
    ("pages", "AboutPageSettings", "overview_image", (1280, 960)),
    ("pages", "Page", "hero_image", (1920, 1200)),
    ("services", "Service", "cover_image", (1280, 960)),
    ("services", "ServiceListPageSettings", "hero_image", (1920, 1200)),
    ("projects", "Project", "cover_image", (1600, 1200)),
    ("projects", "ProjectListPageSettings", "hero_image", (1920, 1200)),
    ("clients", "TrustPageSettings", "hero_image", (1920, 1200)),
    ("documents", "DownloadsPageSettings", "hero_image", (1920, 1200)),
    ("careers", "CareerPageSettings", "hero_image", (1920, 1200)),
    ("inquiries", "ContactPageSettings", "hero_image", (1920, 1200)),
)


class Command(BaseCommand):
    help = "Convert oversized public PNG/JPEG images to compact WebP variants."

    def add_arguments(self, parser):
        parser.add_argument("--quality", type=int, default=78)
        parser.add_argument("--min-bytes", type=int, default=200_000)

    def handle(self, *args, **options):
        from django.apps import apps

        quality = max(55, min(options["quality"], 90))
        minimum = max(50_000, options["min_bytes"])
        converted = 0
        saved_bytes = 0

        for app_label, model_name, field_name, max_size in IMAGE_FIELDS:
            model = apps.get_model(app_label, model_name)
            queryset = model.objects.exclude(**{field_name: ""}).exclude(
                **{f"{field_name}__isnull": True}
            )
            for instance in queryset.iterator():
                image_field = getattr(instance, field_name)
                if not image_field or image_field.name.lower().endswith(".webp"):
                    continue
                try:
                    original_size = image_field.size
                except (FileNotFoundError, OSError, ValueError):
                    continue
                if original_size < minimum:
                    continue

                try:
                    with image_field.storage.open(image_field.name, "rb") as source:
                        image = ImageOps.exif_transpose(Image.open(source))
                        image.load()
                except (FileNotFoundError, OSError, UnidentifiedImageError):
                    continue

                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA" if "transparency" in image.info else "RGB")
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                output = BytesIO()
                image.save(output, "WEBP", quality=quality, method=6)
                optimized = output.getvalue()
                if len(optimized) >= original_size * 0.9:
                    continue

                old_path = PurePosixPath(image_field.name)
                requested_name = str(old_path.with_suffix(".webp"))
                storage = image_field.storage
                new_name = storage.save(requested_name, ContentFile(optimized))
                setattr(instance, field_name, new_name)
                instance.save(update_fields=[field_name])
                converted += 1
                saved_bytes += original_size - len(optimized)

        self.stdout.write(
            self.style.SUCCESS(
                f"Optimized {converted} public images; reduced transfer sources by "
                f"{saved_bytes / (1024 * 1024):.1f} MiB."
            )
        )
