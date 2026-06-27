# Static UI Translation Guide

Upgrade 15 added translation tags to many visible labels and added starter `.po` files:

```text
locale/ar/LC_MESSAGES/django.po
locale/zh_Hans/LC_MESSAGES/django.po
```

## Commands

After installing gettext on your system, run:

```bash
django-admin compilemessages
```

Or regenerate strings:

```bash
django-admin makemessages -l ar
django-admin makemessages -l zh_Hans
django-admin compilemessages
```

## What static translation covers

Static translation covers text hardcoded in templates:

```text
Download
Preview
Request
Contact Us
Dashboard
No services found
Table headers
Form buttons
```

CMS/database content is translated by:

```text
LocalizedContent
```

and seeded by:

```bash
python manage.py seed_localization
```

## Arabic / RTL

Arabic uses:

```html
<html lang="ar" dir="rtl">
```

RTL styling is in:

```text
static/css/rtl.css
```
