# Deployment Guide

## Recommended production layout

```text
https://example.com/          Django website
https://example.com/admin/    Django admin
https://example.com/media/    Media files
https://example.com/static/   Static files
```

## Production checklist

```bash
DEBUG=False
SECRET_KEY=strong-random-secret
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_URL=postgres://user:password@localhost:5432/company_profile

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
python manage.py seed_site
gunicorn config.wsgi:application
```

## Nginx notes

Serve:

```text
/static/ from staticfiles
/media/ from media
proxy all other requests to gunicorn
```

## Security

- Use HTTPS.
- Keep `DEBUG=False`.
- Use a strong admin password.
- Validate file uploads.
- Back up database and media.
- Restrict admin access if possible.


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
