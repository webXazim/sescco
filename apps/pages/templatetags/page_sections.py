from django import template
from django.core.cache import cache
from django.utils.html import format_html

register = template.Library()


def _section_map():
    cached = cache.get("cms_section_order_map")
    if cached is not None:
        return cached
    try:
        from apps.pages.models import PageSectionOrder
        rows = PageSectionOrder.objects.all().values("page_key", "section_key", "sort_order", "is_active")
        mapping = {(row["page_key"], row["section_key"]): row for row in rows}
    except Exception:
        mapping = {}
    cache.set("cms_section_order_map", mapping, 60)
    return mapping


@register.simple_tag
def section_order_value(page_key, section_key, default=100):
    page_key = page_key or "generic"
    section_key = section_key or "custom_sections"
    default = default or 100
    row = _section_map().get((str(page_key), str(section_key)))
    if not row:
        return default
    return row.get("sort_order", default)


@register.simple_tag
def section_attrs(page_key, section_key, default=100):
    page_key = page_key or "generic"
    section_key = section_key or "custom_sections"
    default = default or 100
    row = _section_map().get((str(page_key), str(section_key)))
    sort_order = row.get("sort_order", default) if row else default
    hidden = row and row.get("is_active") is False
    if hidden:
        return format_html('data-page-section="{}" data-section-order="{}" hidden', section_key, sort_order)
    return format_html('data-page-section="{}" data-section-order="{}"', section_key, sort_order)


@register.filter
def active_items(items):
    """Return only active rows for template consistency checks.

    Works with Django related managers/querysets and with ordinary iterables.
    """
    if not items:
        return []
    try:
        return items.filter(is_active=True)
    except Exception:
        try:
            return [item for item in items if getattr(item, "is_active", True)]
        except TypeError:
            return []


@register.filter
def has_items(items):
    """Template-friendly truth test for querysets/lists returned by active_items."""
    if not items:
        return False
    try:
        return items.exists()
    except Exception:
        return bool(items)
