# Upgrade 2 — Project Health Pass

This pass keeps the project Django-template based and improves reliability before continuing feature modules.

## Fixed / improved

- Corrected dashboard links to Django admin app URLs.
- Corrected inquiry model so email can be optional when phone is provided.
- Updated setup instructions to include `makemigrations` before `migrate`.
- Kept the project fully Django-template based, not React SPA.
- Confirmed the build direction: all visible content should be database-driven and editable from Django admin/dashboard.

## Important setup order

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_site
python manage.py runserver
```

## Next upgrade focus

Upgrade 3 should make the core CMS/admin experience stronger:

- Better admin grouping and labels
- Dynamic theme variables
- Improved navigation/footer editing
- Safer singleton settings
- Better seed content and default sections
- Add more reusable content models for homepage/about sections
