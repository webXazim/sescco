# QA Checklist for Standard Company Profile Django CMS

Run these commands after extracting the ZIP:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_site
python manage.py check_cms
python manage.py check
python manage.py runserver
```

## Pages to manually test

```text
/
 /about/
 /services/
 /services/electrical-engineering/
 /projects/
 /projects/fiber-optic-network-project/
 /clients-certifications/
 /downloads/
 /downloads/request/
 /contact/
 /dashboard/
 /admin/
 /sitemap.xml
 /robots.txt
```

## Admin modules to test

```text
Company Profile
Theme Settings
Navigation Menu
Footer Columns / Links
Home Hero
Home About
Home Section Settings
Pages
Services
Projects
Clients
Certificates
Documents
Contact Inquiries
Document Requests
SEO / Robots
Schema Markup
Redirect Rules
```

## Check points

- Header logo and navigation are editable.
- Footer columns and social links are editable.
- Homepage hero and sections are editable.
- Services list and service detail pages are editable.
- Project list and project detail pages are editable.
- Downloads can be previewed, downloaded, or requested.
- Contact form stores inquiries.
- Dashboard opens for staff users.
- Sitemap and robots load.
- Mobile layout is readable.

## Upgrade 127 production data audit

After seeding, run the production data audit before final deployment:

```bash
python manage.py seed_sescco_production --run-audit
python manage.py production_data_audit --strict --output reports/production-data-audit.md
```

Review the generated report for:

- missing page, service, project or document content
- empty enabled CMS sections
- missing service FAQs or brochure files
- missing project scope items or metrics
- missing Arabic / Chinese localization rows
- missing SEO metadata


## Upgrade 128 media and asset checks

- Run `python manage.py production_asset_audit --strict --output reports/production-asset-audit.md` before deployment.
- Open Home, Services, Projects, Downloads, Trust & Compliance, and About pages with browser cache disabled.
- Temporarily remove one test media file locally and confirm the SESCCO fallback visual appears instead of a blank or broken card.
- Confirm lazy images still appear correctly in English, Arabic RTL, and Chinese pages.
- Confirm service and project cards keep a stable height on mobile while images load.

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

## Upgrade 130 admin production safety

- Run `python manage.py production_admin_audit --strict --output reports/production-admin-audit.md`.
- Confirm singleton settings have only one row each.
- Confirm public slugs are unique before deployment.
- Confirm active admin content has no empty title, slug, body, FAQ, or CTA fields.


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
