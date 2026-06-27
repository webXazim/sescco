# SESCCO Production Data Audit

Summary: **0 error(s)**, **11 warning(s)**, **11 total finding(s)**.

## Record Coverage

- **active_certificates**: 4
- **active_clients**: 29
- **active_documents**: 11
- **active_navigation_items**: 7
- **active_page_sections**: 6
- **active_partners**: 4
- **active_projects**: 19
- **active_service_categories**: 5
- **active_services**: 5
- **active_trust_metrics**: 6
- **company_profiles**: 1
- **featured_projects**: 6
- **home_highlights**: 3
- **localized_rows_ar**: 1585
- **localized_rows_zh_hans**: 1585
- **page_faqs**: 11
- **project_list_stats**: 5
- **published_pages**: 5
- **service_list_faqs**: 4
- **site_settings**: 1
- **why_choose_items**: 4

## Findings

- [WARN] Services: At least 6 active production services are recommended.
- [WARN] Documents: ISO Certification Pack: file is not attached.
- [WARN] Documents: Vendor Registration Information: file is not attached.
- [WARN] Localization: faq: 4 active object(s) missing ar localization rows.
- [WARN] Localization: faq: 4 active object(s) missing zh-hans localization rows.
- [WARN] Localization: projectmetric: 82 active object(s) missing ar localization rows.
- [WARN] Localization: projectmetric: 82 active object(s) missing zh-hans localization rows.
- [WARN] Localization: downloaddocument: 2 active object(s) missing ar localization rows.
- [WARN] Localization: downloaddocument: 2 active object(s) missing zh-hans localization rows.
- [WARN] Localization: certificate: 4 active object(s) missing ar localization rows.
- [WARN] Localization: certificate: 4 active object(s) missing zh-hans localization rows.

## Recommended command sequence

```bash
python manage.py migrate
python manage.py seed_sescco_production --run-audit
python manage.py production_data_audit --strict --output reports/production-data-audit.md
python manage.py collectstatic --noinput
```
