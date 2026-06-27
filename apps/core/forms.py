from django import forms
from .models import LocalizedContent
from .translation_registry import get_target


class LocalizedContentAdminForm(forms.ModelForm):
    class Meta:
        model = LocalizedContent
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        content_type = cleaned.get("content_type")
        field_name = cleaned.get("field_name")
        target = get_target(content_type)
        if target and field_name and field_name not in target.fields:
            raise forms.ValidationError(
                f"'{field_name}' is not registered for {target.model_label}. Allowed fields: {', '.join(target.fields)}"
            )
        return cleaned
