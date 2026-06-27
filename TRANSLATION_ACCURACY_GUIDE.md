# Translation Accuracy Guide

The site now supports full localization technically, but translation quality depends on accurate translation content.

## Important

Earlier upgrades used demo translations such as:

```text
ترجمة: English text
```

Upgrade 19 removes those and replaces them with cleaner meaning-based seed translations.

## What should stay unchanged

Some values should not be translated:

```text
Company abbreviations
Brand/client names
Phone numbers
Emails
Vendor codes
Certificate numbers
File version numbers
```

Examples:

```text
aramco
SABIC
+966...
info@...
10114560
```

## What should be translated

```text
Hero titles
Subtitles
Descriptions
Service names
Project summaries
Button text
Form labels
Section headings
FAQ content
CTA text
```

## Commands

```bash
python manage.py seed_localization
python manage.py localization_qa
```

## Best client workflow

For final delivery, the client should review:

```text
/dashboard/translations/
/admin/core/localizedcontent/
```

Because machine/demo translation is never equal to professionally reviewed business translation.

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
