from .models import SchemaMarkup


def schema_context(request):
    return {
        "schema_markups": SchemaMarkup.objects.filter(is_active=True).filter(page_path__in=["", request.path])
    }
