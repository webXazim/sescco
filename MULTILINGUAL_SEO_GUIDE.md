# Multilingual SEO Guide

Upgrade 16 adds multilingual SEO support.

## URLs

```text
/                 English
/ar/              Arabic
/zh-hans/         Chinese
/localized-sitemap.xml
/robots.txt
```

## SEO tags

Every public page now includes:

```html
<link rel="canonical" ...>
<link rel="alternate" hreflang="en" ...>
<link rel="alternate" hreflang="ar" ...>
<link rel="alternate" hreflang="zh-Hans" ...>
<link rel="alternate" hreflang="x-default" ...>
```

## Localized meta fields

Use `LocalizedContent` records for:

```text
seo_title
seo_description
```

Supported on:

```text
Page
Service
Project
```

## Sitemap

The standard sitemap remains:

```text
/sitemap.xml
```

The language-aware URL list is:

```text
/localized-sitemap.xml
```

## QA commands

```bash
python manage.py localization_qa
python manage.py translation_report --language ar
python manage.py translation_report --language zh-hans
```

## Manual QA

Check page source for:

```text
canonical
hreflang
og:locale
application/ld+json
```

Check language pages:

```text
/ar/
/zh-hans/
/ar/services/
/zh-hans/projects/
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
