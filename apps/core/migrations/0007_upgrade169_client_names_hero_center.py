from django.db import migrations


PROPER_AR = {
    "EPC": "إي بي سي",
    "DACO": "داكو",
    "BCC": "بي سي سي",
    "NHC": "إن إتش سي",
    "SEC": "إس إي سي",
    "STC": "إس تي سي",
    "TR": "تي آر",
    "ABRAR": "أبرار",
    "Abahsain Consolidating Co": "أبهسين كونسوليديتنغ كو.",
    "Abahsain Consolidated Co": "أبهسين كونسوليديتد كو.",
    "Energy & Power Cont. Co. Ltd": "إنرجي آند باور كونتراكتنغ كو. ليمتد",
    "Energy & Power Cont. Co": "إنرجي آند باور كونتراكتنغ كو.",
    "Energy & Power Contracting Co": "إنرجي آند باور كونتراكتنغ كو.",
    "Saudi National Bank": "سعودي ناشونال بنك",
    "Seven Entertainment Ventures": "سفن إنترتينمنت فينتشرز",
    "Saudi Electricity Company": "سعودي إلكتريسيتي كومباني",
    "Saudi Energy": "سعودي إنرجي",
    "SEPCO": "سيبكو",
    "SINOMA": "سينوما",
    "Royal Comision": "رويال كومشن",
    "Royal Commission": "رويال كومشن",
    "SAIPEM": "سايبم",
    "SABIC": "سابك",
    "Novartis": "نوفارتس",
    "Riyadh Airport Company": "رياض إيربورت كومباني",
    "Riyadh Airports Company": "رياض إيربورتس كومباني",
    "McDermott": "ماكديرموت",
    "MOBILY": "موبايلي",
    "Havelock1": "هافلوك ون",
    "Havelock One": "هافلوك ون",
    "L & T": "إل آند تي",
    "L&T": "إل آند تي",
    "ZAIN": "زين",
}


def set_loc(LocalizedContent, obj, lang, field, text):
    if not obj or not getattr(obj, "id", None):
        return
    LocalizedContent.objects.update_or_create(
        content_type=obj.__class__.__name__.lower(),
        object_id=obj.id,
        language_code=lang,
        field_name=field,
        defaults={"text": text},
    )


def repair(apps, schema_editor):
    LocalizedContent = apps.get_model("core", "LocalizedContent")
    Client = apps.get_model("clients", "Client")
    ProjectMetric = apps.get_model("projects", "ProjectMetric")

    for client in Client.objects.all():
        ar = PROPER_AR.get(client.name)
        if ar:
            set_loc(LocalizedContent, client, "ar", "name", ar)
        set_loc(LocalizedContent, client, "zh-hans", "name", client.name)

    for metric in ProjectMetric.objects.all():
        ar = PROPER_AR.get(metric.value)
        if ar:
            set_loc(LocalizedContent, metric, "ar", "value", ar)
        set_loc(LocalizedContent, metric, "zh-hans", "value", metric.value)


class Migration(migrations.Migration):
    dependencies = [("core", "0006_upgrade168_proper_names")]
    operations = [migrations.RunPython(repair, migrations.RunPython.noop)]
