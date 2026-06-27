from django.db import migrations


PROPER_AR = {
    "ARAMCO": "أرامكو",
    "Abahsain Consolidating Co.": "أبهسين كونسوليديتنغ كو.",
    "Abahsain Consolidated Co.": "أبهسين كونسوليديتد كو.",
    "Al Rajhi Bank": "الراجحي بنك",
    "ABRAR": "أبرار",
    "Energy & Power Cont. Co. Ltd.": "إنرجي آند باور كونتراكتنغ كو. ليمتد",
    "EPC": "EPC",
    "DACO": "DACO",
    "BCC": "BCC",
    "MOBILY": "موبايلي",
    "McDermott": "ماكديرموت",
    "L & T": "إل آند تي",
    "Havelock1": "هافلوك ون",
    "Havelock One": "هافلوك ون",
    "Rommel Electro Arabia": "روميل إلكترو أرابيا",
    "Riyadh Airport Company": "رياض إيربورت كومباني",
    "Novartis": "نوفارتس",
    "NHC": "NHC",
    "Royal Comision": "رويال كومشن",
    "SABIC": "سابك",
    "SAIPEM": "سايبم",
    "Saudi Energy": "سعودي إنرجي",
}


def repair(apps, schema_editor):
    LocalizedContent = apps.get_model("core", "LocalizedContent")
    Client = apps.get_model("clients", "Client")
    for client in Client.objects.all():
        ar = PROPER_AR.get(client.name)
        if ar:
            LocalizedContent.objects.update_or_create(
                content_type="client",
                object_id=client.id,
                language_code="ar",
                field_name="name",
                defaults={"text": ar},
            )
        LocalizedContent.objects.update_or_create(
            content_type="client",
            object_id=client.id,
            language_code="zh-hans",
            field_name="name",
            defaults={"text": client.name},
        )


class Migration(migrations.Migration):
    dependencies = [("core", "0005_upgrade167_localization_polish")]
    operations = [migrations.RunPython(repair, migrations.RunPython.noop)]
