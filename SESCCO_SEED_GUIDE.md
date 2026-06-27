# SESCCO One-Command Production Seed

Use this single command after migrations to load the production-ready English content, bundled client logo placeholders, bundled certificate preview images, and localization records:

```bash
python manage.py seed_sescco_production
```

## What it does
- seeds core site/company settings
- seeds home/about/services/projects/clients/careers content
- seeds featured client entries with bundled logo placeholders
- seeds featured certificate entries with bundled preview images
- seeds localization content for multilingual pages

## English only
If you only want the English CMS content:

```bash
python manage.py seed_sescco_production --skip-localization
```


The command `python manage.py reset_sescco_seed` is still available as the underlying reset/reseed command.

## Seed with production audit

Upgrade 127 adds an optional audit step after the one-command seed:

```bash
python manage.py seed_sescco_production --run-audit
```

For stricter deployment checks, use:

```bash
python manage.py seed_sescco_production --strict-audit
```

To save a Markdown report:

```bash
python manage.py production_data_audit --output reports/production-data-audit.md
```


## Upgrade 128 asset audit

After seeding, run the asset audit to make sure CMS media, document files, logos, thumbnails, and required static fallback assets are not broken:

```bash
python manage.py production_asset_audit --strict --output reports/production-asset-audit.md
```

For a static-only deployment smoke test, use:

```bash
python manage.py production_asset_audit --skip-media --strict
```

## Upgrade 129 — multilingual content accuracy guard

Run this after seeding whenever English, Arabic, or Chinese CMS content changes:

```bash
python manage.py multilingual_content_audit --strict --output reports/multilingual-content-audit.md
```

For a full production seed and verification pass, use:

```bash
python manage.py migrate
python manage.py seed_sescco_production --run-audit --run-language-audit --run-asset-audit
python manage.py production_data_audit --strict --output reports/production-data-audit.md
python manage.py multilingual_content_audit --strict --output reports/multilingual-content-audit.md
python manage.py production_asset_audit --strict --output reports/production-asset-audit.md
python manage.py collectstatic --noinput
```

The language audit checks Arabic/Chinese row coverage, exact English copies, placeholder translation text, suspiciously short translated copy, Latin-heavy Arabic/Chinese rows, and field-level parity for public CMS objects.

## Upgrade 130 admin safety audit

After seeding, run:

```bash
python manage.py seed_sescco_production --run-audit --run-language-audit --run-asset-audit --run-admin-audit
python manage.py production_admin_audit --strict --output reports/production-admin-audit.md
```

Use `--strict-admin-audit` during final deployment to fail early when duplicate singleton rows or duplicate slugs are found.


## Upgrade 131 Final Deployment QA Hardening

Final pre-launch command:

```bash
python manage.py migrate
python manage.py seed_sescco_production --run-audit --run-language-audit --run-asset-audit --run-admin-audit --run-final-audit
python manage.py production_data_audit --strict --output reports/production-data-audit.md
python manage.py multilingual_content_audit --strict --output reports/multilingual-content-audit.md
python manage.py production_asset_audit --strict --output reports/production-asset-audit.md
python manage.py production_admin_audit --strict --output reports/production-admin-audit.md
python manage.py final_deployment_audit --strict --output reports/final-deployment-audit.md
python manage.py collectstatic --noinput
```

Confirm `/healthz/`, `/sitemap.xml`, `/localized-sitemap.xml`, `/robots.txt`, English, Arabic, Chinese, mobile, contact form, career application, downloads, and error pages before launch.
