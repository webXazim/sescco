# Translation Admin Workflow

## Where to manage translations

Open:

```text
/dashboard/translations/
/admin/core/localizedcontent/
```

## Recommended workflow

1. Create normal English/default content from each module admin.
2. Run:

```bash
python manage.py seed_localization
```

3. Open:

```text
/dashboard/translations/
```

4. Filter by Arabic or Chinese.
5. Edit translation records in:

```text
/admin/core/localizedcontent/
```

## What each translation record means

```text
content_type = service
object_id = 3
language_code = ar
field_name = title
text = translated Arabic title
```

## Useful commands

```bash
python manage.py translation_report --language ar
python manage.py translation_report --language zh-hans
python manage.py seed_localization
```

## Important note

This project currently uses the safe override translation system:

```text
LocalizedContent
```

This is safer than converting every model to tabbed `django-parler` immediately. It allows us to localize existing CMS content without breaking all existing migrations and data.

## Next possible upgrade

The next upgrade can add a proper UI that groups translations by object, showing English on the left and Arabic/Chinese input on the right.
