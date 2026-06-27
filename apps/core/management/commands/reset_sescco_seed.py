from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Reset and reseed SESCCO production English content and localization records."

    def add_arguments(self, parser):
        parser.add_argument("--skip-localization", action="store_true", help="Only seed English CMS content.")

    def handle(self, *args, **options):
        call_command("seed_site")
        if not options["skip_localization"]:
            call_command("seed_localization")
        self.stdout.write(self.style.SUCCESS("SESCCO CMS seed reset completed."))
