from django.db import migrations


def set_loc(LocalizedContent, obj, lang, field, text):
    LocalizedContent.objects.update_or_create(
        content_type=obj.__class__.__name__.lower(),
        object_id=obj.id,
        language_code=lang,
        field_name=field,
        defaults={"text": text},
    )


def forwards(apps, schema_editor):
    LocalizedContent = apps.get_model("core", "LocalizedContent")
    ServiceCTA = apps.get_model("services", "ServiceCTA")
    for cta in ServiceCTA.objects.all():
        set_loc(LocalizedContent, cta, "ar", "title", "هل تحتاج إلى دعم لهذا العمل؟")
        set_loc(LocalizedContent, cta, "ar", "subtitle", "تواصل مع SESCCO لمناقشة متطلبات مشروعك.")
        set_loc(LocalizedContent, cta, "ar", "button_text", "اطلب عرضاً")
        set_loc(LocalizedContent, cta, "zh-hans", "title", "需要此项工作的支持？")
        set_loc(LocalizedContent, cta, "zh-hans", "subtitle", "请联系 SESCCO 讨论您的项目需求。")
        set_loc(LocalizedContent, cta, "zh-hans", "button_text", "获取报价")


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [("services", "0001_initial"), ("core", "0004_sitesettings_footer_social_developer_credit")]
    operations = [migrations.RunPython(forwards, backwards)]
