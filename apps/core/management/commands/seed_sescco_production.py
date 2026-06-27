from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "One-command SESCCO production seed including localization."

    def add_arguments(self, parser):
        parser.add_argument("--skip-localization", action="store_true", help="Only seed English CMS content.")
        parser.add_argument("--run-audit", action="store_true", help="Run production_data_audit after seeding.")
        parser.add_argument("--strict-audit", action="store_true", help="Fail the command if the post-seed audit finds production-blocking errors.")
        parser.add_argument("--run-asset-audit", action="store_true", help="Run production_asset_audit after seeding.")
        parser.add_argument("--strict-asset-audit", action="store_true", help="Fail the command if referenced CMS/static assets are missing.")
        parser.add_argument("--run-language-audit", action="store_true", help="Run multilingual_content_audit after seeding.")
        parser.add_argument("--strict-language-audit", action="store_true", help="Fail when blocking Arabic/Chinese localization quality issues are found.")
        parser.add_argument("--run-admin-audit", action="store_true", help="Run production_admin_audit after seeding.")
        parser.add_argument("--strict-admin-audit", action="store_true", help="Fail when duplicate singletons, duplicate slugs, or other admin safety blockers are found.")
        parser.add_argument("--run-final-audit", action="store_true", help="Run final_deployment_audit after all post-seed checks.")
        parser.add_argument("--strict-final-audit", action="store_true", help="Fail when final deployment settings, templates, URLs or child audits fail.")

    def handle(self, *args, **options):
        call_command("sync_page_section_order", prune_obsolete=True)
        call_command("reset_sescco_seed", skip_localization=options["skip_localization"])
        call_command("sync_page_section_order", prune_obsolete=True)
        if options.get("run_audit") or options.get("strict_audit"):
            call_command("production_data_audit", strict=options.get("strict_audit", False))
        if options.get("run_asset_audit") or options.get("strict_asset_audit"):
            call_command("production_asset_audit", strict=options.get("strict_asset_audit", False))
        if options.get("run_language_audit") or options.get("strict_language_audit"):
            call_command("multilingual_content_audit", strict=options.get("strict_language_audit", False))
        if options.get("run_admin_audit") or options.get("strict_admin_audit"):
            call_command("production_admin_audit", strict=options.get("strict_admin_audit", False))
        if options.get("run_final_audit") or options.get("strict_final_audit"):
            call_command("final_deployment_audit", strict=options.get("strict_final_audit", False), skip_child_audits=True)
        self.stdout.write(self.style.SUCCESS("SESCCO production seed completed with section-order sync and optional production audits."))
