# Standard Company Profile Django CMS — V1

A reusable Django template-based company profile website CMS.

## What is included

- Django project structure
- CRUD models for company profile, pages, services, projects, clients, certifications, documents, inquiries
- Dynamic Django templates
- Reusable header/footer/CTA includes
- CKEditor 5 for rich text fields
- Admin CRUD setup
- Contact inquiry form
- Dashboard overview
- Seed command with SESCCO sample content

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_site
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
http://127.0.0.1:8000/dashboard/
```

## Main principle

Everything visible on the website should be editable from Django admin/dashboard unless it is pure structural UI.

## Build status

This is Upgrade 2 / Project Health Build. It improves the foundation with safer setup instructions, fixes template/admin path issues, and corrects inquiry email validation so phone-only inquiries can work. It creates the complete base and makes all major pages dynamic enough to continue improving page-by-page.

Recommended next upgrades:

1. Polish template visual matching against static prototype
2. Improve homepage section builder
3. Improve service detail and projects detail layouts
4. Add custom dashboard CRUD screens
5. Add SEO sitemap/robots and production settings

## Upgrade 3 — Core CMS Polish

This version improves the global CMS layer:

- Added CRUD models for reusable site assets
- Added CRUD trust metrics for homepage/about strips
- Added reusable CTA sections
- Added office locations
- Added business hours
- Added contact methods for footer/contact page
- Footer now uses ContactMethod, OfficeLocation, FooterColumn and SocialLink data
- Contact page now uses dynamic contact methods, offices and business hours
- Homepage trust strip now uses TrustMetric records
- Contact form email is optional if phone is provided
- Seed command now creates all core CMS defaults

Run after upgrading:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
```

## Upgrade 4 — Homepage Fully CRUD

This version makes the homepage much more database-driven.

Added editable admin modules:

- Home Hero
- Home About Block
- Home Section Settings
- Why Choose Items
- Home Highlights

Homepage now uses reusable include templates:

- `includes/home_hero.html`
- `includes/trust_strip.html`
- `includes/home_highlights.html`
- `includes/home_about.html`
- `includes/why_choose_grid.html`
- `includes/dynamic_page_sections.html`

Admin can now control:

- Hero title, subtitle, image, buttons
- About preview text, image and button
- Section headings and visibility
- Featured item limits
- Why choose us cards
- Highlights/cards below the trust strip
- Custom homepage sections through PageSection

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
```

## Upgrade 5 — Pages, About, and Reusable Page Sections

This upgrade improves the page CMS layer.

Added editable modules:

- About Page Settings
- Mission / Vision Items
- Value Items
- Leadership Messages
- Generic Page Settings

Improved:

- About page is now fully section-controlled
- Generic pages can have width/sidebar settings
- FAQs render as expandable details
- Page sections are reusable
- Timeline/stats/mission/values/leadership are all admin-editable

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
```

## Upgrade 6 — Services Module Completion

This upgrade makes services much closer to a full reusable CMS module.

Added:

- Service List Page Settings
- Service Detail Page Settings
- Service List Process Steps
- Service List FAQs
- Service Key Points
- Service Features
- Service CTA

Improved:

- Services overview hero and intro are editable
- Search/category visibility is editable
- Service listing process and FAQs are editable
- Service detail hero uses service cover image
- Key points, deliverables, features, process, FAQs, brochure and CTA are all CRUD-based
- Service admin has richer inline editing
- Dashboard links updated

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
```

## Upgrade 7 — Projects Module Completion

This upgrade makes the projects module a full case-study CMS.

Added:

- Project List Page Settings
- Project Detail Page Settings
- Project List Stats
- Project Scope Items
- Project Documents
- Project CTA

Improved:

- Project listing hero and intro are editable
- Project stats strip is editable
- Project filters support category, status, year and search
- Featured project block is editable through featured project flag
- Project detail has quick facts, gallery, case study blocks, scope items, metrics, documents, CTA and related projects
- Project admin has richer inline editing
- Dashboard links updated

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
```

## Upgrade 8 — Clients, Certifications, Partners and Trust Module

This upgrade completes the trust/credibility page.

Added:

- Trust Page Settings
- Trust Metrics
- Client Categories
- Certificate Categories
- Compliance Blocks
- Certificate expiry display
- Better trust page include templates

Improved:

- Clients page hero is editable
- Client category tabs are dynamic
- Partners section is dynamic
- Certificates show expiry/expired status
- Accreditations, standards, compliance, testimonials and documents are modular
- Dashboard links updated

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
```

## Upgrade 9 — Documents + Contact/Inquiries Completion

This upgrade completes the documents/downloads and contact workflow.

Added:

- Downloads Page Settings
- Document Page CTA
- Document Request Form and page
- Contact Page Settings
- Document access levels: public/request/private
- Preview toggle
- Inquiry technical fields: IP, user agent, spam suspicion

Improved:

- Downloads page hero, intro, filters and table are editable
- Document preview/download/request behavior is clearer
- Download count and logs continue to work
- Contact page hero, contact methods, offices, hours, map, FAQ and WhatsApp CTA are editable
- Inquiry admin has better status/spam workflow
- Dashboard links updated

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
```

## Upgrade 10 — Dashboard, SEO, Error Pages and Production Polish

Added:

- SEO app
- Robots.txt settings
- Sitemap.xml
- Redirect rules model
- Schema markup model
- 404 and 500 templates
- Improved dashboard overview
- Activity log signals
- Dockerfile
- docker-compose.yml
- DEPLOYMENT.md

Important URLs:

```text
/sitemap.xml
/robots.txt
/dashboard/
/admin/
```

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
python manage.py collectstatic
```

## Upgrade 11 — QA/Fix Pass

This upgrade focuses on project health and safer setup.

Fixed/improved:

- Normalized dashboard AppConfig and signal loading
- Added redirect middleware for SEO redirect rules
- Added schema markup context processor and template rendering
- Improved generic page template safety
- Improved inquiry and document request forms
- Added `check_cms` setup validation command
- Added `QA_CHECKLIST.md`
- Ran Python syntax compile check on all project `.py` files during packaging

Recommended commands:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
python manage.py check_cms
python manage.py check
python manage.py runserver
```


## Upgrade 12 — Localization Architecture

Added:

- Django i18n configuration
- `django-parler` dependency and settings
- Language-prefixed public URLs
- Language switcher in header
- Arabic RTL support
- `LocalizedContent` override model
- Localization template tags
- Locale folders for Arabic and Chinese
- `LOCALIZATION_GUIDE.md`
- `seed_localization` command

Useful commands:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
python manage.py seed_localization
python manage.py runserver
```

Translation commands:

```bash
django-admin makemessages -l ar
django-admin makemessages -l zh_Hans
django-admin compilemessages
```

## Upgrade 12 Template Fix

Fixed template ordering issue where `{% load i18n %}` appeared before `{% extends "base.html" %}`. Django requires `{% extends %}` to be the first template tag in child templates.

## Upgrade 12 Language Switcher Fix

Fixed:

- Arabic page could not switch back to English/Chinese because the switcher posted to the same current path.
- Homepage CMS fields did not use localization overrides.
- `seed_localization` now creates useful homepage/navigation/CTA translations.

Run:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py seed_site
python manage.py seed_localization
python manage.py runserver
```

Then test:

```text
/
 /ar/
 /zh-hans/
```

## Upgrade 13 — Full Visible Model Localization Pass

Connected remaining visible CMS components to localization overrides and rebuilt `seed_localization` to generate Arabic/Chinese sample translations across the site.

## Upgrade 14 — Translation Admin Workflow

Added a translation registry, improved LocalizedContent admin, a staff translation dashboard, report commands, and `TRANSLATION_ADMIN_WORKFLOW.md`.

## Upgrade 15 — Static Text and RTL/Chinese UI Polish

Added more `{% trans %}` tags, starter Arabic/Chinese `.po` files, RTL layout improvements, Arabic/Chinese font fallbacks, table alignment, arrow direction fixes, and mobile language switcher polish.

## Upgrade 16 — Multilingual SEO + Final Localization QA

Added canonical/hreflang tags, localized meta helpers, localized sitemap, query-preserving language switcher URLs, localized Organization schema, `localization_qa` command, and `MULTILINGUAL_SEO_GUIDE.md`.

## Upgrade 17 — Language Persistence + About/Global Localization Fix

Fixed internal links switching back to default language and added explicit About page/trust metric translations.

## Upgrade 18 — Full Site Localization Completion Pass

Cleaned old mixed English demo translations, added cleaner Arabic/Chinese seed content across all modules, connected remaining trust/category fields, and improved localization QA checks.

## Upgrade 19 — Meaning-Accurate Localization Pass

Replaced generic demo localization with meaning-based Arabic/Chinese seed content, preserved proper names/phone/email/code values, localized form labels without relying on compilemessages, and added `TRANSLATION_ACCURACY_GUIDE.md`.

## Upgrade 20 — CMS Localization Hardening Pass

Added `static_text` template localization helper, replaced remaining hardcoded English labels on contact/document/project/trust sections, and improved QA guidance for static vs CMS localization.

## Upgrade 21 — SESCCO Production English Seed + Localization Seed Reset

Rebuilt `seed_site` with SESCCO production English content, rebuilt `seed_localization` as its Arabic/Chinese counterpart, and added `reset_sescco_seed` plus `SESCCO_SEED_GUIDE.md`.

## Upgrade 22 — Homepage UX/UI Polish + Admin Hero Photo

Added a production-grade homepage hero with an admin-editable engineers photo, right-side light-blue visual panel, floating vendor badges, responsive layout and Arabic RTL layout swap.

## Upgrade 23 — Hero Background Blend Polish

Updated the homepage hero so the engineers photo blends into the light-blue right-side visual area as a background panel instead of appearing like a standalone image card. RTL/mobile behavior was polished as well.

## Upgrade 24 — Hero Match to Original Blue Shade

Refined the homepage hero to more closely match the earlier blue-shade design while keeping the engineers photo as a subtle admin-editable background visual.

## Upgrade 25 — Final Homepage Hero Direction

Decided and implemented the final homepage hero style: original clean blue-shade template feeling, with the engineers photo softly blended as a background visual, not a separate card.

## Upgrade 26 — Arabic Hero Layout Fit Fix

Fixed Arabic homepage hero alignment so the blue/photo visual stays on the left and Arabic content stays cleanly on the right, with improved Arabic headline sizing.

## Upgrade 27 — Sitewide Logo Integration + Homepage Polish Review

Added the uploaded SESCCO SVG logo sitewide through a reusable logo include, seeded it into CompanyProfile.logo when empty, and slightly polished homepage hero image visibility while preserving the blue-shade design.

## Upgrade 28 — A-Z SESCCO Production Polish Pass

Removed generic demo home cards, enforced SESCCO-specific production seed data, strengthened sitewide logo usage, and added `production_qa` for readiness checks.

## Upgrade 29 — Seed Localization Import Fix

Fixed missing `HomeHighlight` import in `seed_localization.py` that caused `reset_sescco_seed` to fail.

## Upgrade 30 — Visible Production Seed Override + Full Header Logo Fix

Added final seed override to remove visible generic CMS/CRUD cards after older logic runs, added full logo lockup with mark + SESCCO text, and strengthened production QA.

## Upgrade 31 — Follow Uploaded Prototype Design System Pass

Added `prototype_alignment.css` based on the uploaded SESCCO static prototype, stored prototype files under `docs/prototype_reference`, and preserved our current CMS/logo/localization/hero modifications.

## Upgrade 32 — Seed Site Helper Fix

Restored missing `update_or_create` helper in `seed_site.py` and made the final HomeHighlight override safer.

## Upgrade 33 — Seed Localization Helpers Fix

Restored missing `set_loc`, `set_many`, and `clean_old_demo_values` helpers in `seed_localization.py`.

## Upgrade 34 — Template Static Quote Fix

Fixed invalid escaped quotes in `base.html` for the `prototype_alignment.css` static tag and added `template_qa`.

## Final admin safety command

```bash
python manage.py production_admin_audit --strict --output reports/production-admin-audit.md
```

This checks duplicate singleton settings, duplicate slugs, empty active CMS records, and risky ordering before deployment.


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
# sescco
# sescco
