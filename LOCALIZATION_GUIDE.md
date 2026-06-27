# Localization Guide

This project now supports localization using Django i18n, language-prefixed URLs, Arabic RTL CSS, a header language switcher, django-parler settings, and a safe CMS translation override model.

## Supported languages

```python
LANGUAGES = [
    ("en", "English"),
    ("ar", "Arabic"),
    ("zh-hans", "Chinese"),
]
```

## URLs

English default:

```text
/
 /services/
```

Other languages:

```text
/ar/
/ar/services/
/zh-hans/
/zh-hans/services/
```

## Static template text

Use:

```django
{% load i18n %}
{% trans "Services" %}
```

Commands:

```bash
django-admin makemessages -l ar
django-admin makemessages -l zh_Hans
django-admin compilemessages
```

## CMS/database content

Use **Core > Localized Content Overrides** in Django admin.

Fields:

```text
content_type: service, project, page, navigationmenu, footerlink, etc.
object_id: the database ID
language_code: ar / zh-hans
field_name: title / body / short_description / hero_title, etc.
text: translated content
```

Example:

```text
content_type = service
object_id = 3
language_code = ar
field_name = title
text = الهندسة الكهربائية
```

Template usage:

```django
{% load localization %}
{% localized_plain service "title" %}
{% localized service "body" as body %}{{ body|safe }}
```

## Why this approach?

This is a safe architecture upgrade because the project already has many CMS models. Full conversion to `TranslatableModel` can be done later model-by-model, but the override model lets you localize immediately without risking data loss or complex migrations.

## Arabic RTL

Arabic pages automatically use:

```html
<html lang="ar" dir="rtl">
```

RTL styles are in:

```text
static/css/rtl.css
```

## Important fix in this version

The language switcher now uses direct URLs:

```text
/          English
/ar/       Arabic
/zh-hans/  Chinese
```

After running:

```bash
python manage.py seed_localization
```

the homepage hero, homepage about block, navigation, CTA, services and project cards should show sample Arabic/Chinese overrides.

## Why not everything is translated automatically?

This CMS does not auto-translate every database field. It uses `LocalizedContent` overrides. For every field you want translated, add an override from Django admin or extend `seed_localization`.

Example:

```text
content_type = homehero
object_id = 1
language_code = ar
field_name = title
text = Arabic title
```
