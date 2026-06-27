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
    ProjectMetric = apps.get_model("projects", "ProjectMetric")
    ProjectCTA = apps.get_model("projects", "ProjectCTA")

    label_ar = {"Location": "الموقع", "Status": "الحالة", "Duration": "المدة", "Client": "العميل", "Contractor": "المقاول", "Year": "السنة", "Category": "الفئة"}
    label_zh = {"Location": "地点", "Status": "状态", "Duration": "周期", "Client": "客户", "Contractor": "承包商", "Year": "年份", "Category": "类别"}
    value_ar = {
        "Completed": "مكتمل", "Complete": "مكتمل", "Ongoing": "قيد التنفيذ", "Planned": "مخطط",
        "6 Months (June 2025)": "6 أشهر (يونيو 2025)", "7 Months (April 2026)": "7 أشهر (أبريل 2026)",
        "8 Months (April 2025)": "8 أشهر (أبريل 2025)", "8 Months (May 2025)": "8 أشهر (مايو 2025)",
        "6 Months (July 2025)": "6 أشهر (يوليو 2025)", "Completed May 2025": "اكتمل في مايو 2025",
        "12 Months (Completed June 2023)": "12 شهراً (اكتمل في يونيو 2023)", "18 Months (Completed October 2024)": "18 شهراً (اكتمل في أكتوبر 2024)",
        "Starting 2025/2026": "بدأ في 2025/2026", "Completed October 2016": "اكتمل في أكتوبر 2016", "Completed August 2016": "اكتمل في أغسطس 2016",
        "Project Completed": "المشروع مكتمل", "Saudi Arabia": "المملكة العربية السعودية", "Yanbu, Saudi Arabia": "ينبع، المملكة العربية السعودية",
        "Jubail, Saudi Arabia": "الجبيل، المملكة العربية السعودية", "Jafurah, Saudi Arabia": "الجافورة، المملكة العربية السعودية",
        "Riyadh, Saudi Arabia": "الرياض، المملكة العربية السعودية", "Haradh, Saudi Arabia": "حرض، المملكة العربية السعودية", "Al Khobar, Saudi Arabia": "الخبر، المملكة العربية السعودية",
    }
    value_zh = {
        "Completed": "已完成", "Complete": "已完成", "Ongoing": "进行中", "Planned": "计划中",
        "6 Months (June 2025)": "6 个月（2025 年 6 月）", "7 Months (April 2026)": "7 个月（2026 年 4 月）",
        "8 Months (April 2025)": "8 个月（2025 年 4 月）", "8 Months (May 2025)": "8 个月（2025 年 5 月）",
        "6 Months (July 2025)": "6 个月（2025 年 7 月）", "Completed May 2025": "2025 年 5 月完成",
        "12 Months (Completed June 2023)": "12 个月（2023 年 6 月完成）", "18 Months (Completed October 2024)": "18 个月（2024 年 10 月完成）",
        "Starting 2025/2026": "2025/2026 年开始", "Completed October 2016": "2016 年 10 月完成", "Completed August 2016": "2016 年 8 月完成",
        "Project Completed": "项目已完成", "Saudi Arabia": "沙特阿拉伯", "Yanbu, Saudi Arabia": "延布，沙特阿拉伯",
        "Jubail, Saudi Arabia": "朱拜勒，沙特阿拉伯", "Jafurah, Saudi Arabia": "贾富拉，沙特阿拉伯",
        "Riyadh, Saudi Arabia": "利雅得，沙特阿拉伯", "Haradh, Saudi Arabia": "哈拉德，沙特阿拉伯", "Al Khobar, Saudi Arabia": "胡拜尔，沙特阿拉伯",
    }
    for metric in ProjectMetric.objects.all():
        if metric.label in label_ar:
            set_loc(LocalizedContent, metric, "ar", "label", label_ar[metric.label])
            set_loc(LocalizedContent, metric, "zh-hans", "label", label_zh[metric.label])
        if metric.value in value_ar:
            set_loc(LocalizedContent, metric, "ar", "value", value_ar[metric.value])
            set_loc(LocalizedContent, metric, "zh-hans", "value", value_zh[metric.value])

    for cta in ProjectCTA.objects.all():
        set_loc(LocalizedContent, cta, "ar", "title", "هل لديك مشروع مشابه؟")
        set_loc(LocalizedContent, cta, "ar", "subtitle", "تواصل مع SESCCO لمناقشة متطلباتك الهندسية أو التعاقدية.")
        set_loc(LocalizedContent, cta, "ar", "button_text", "ابدأ مشروعاً")
        set_loc(LocalizedContent, cta, "zh-hans", "title", "需要类似项目支持？")
        set_loc(LocalizedContent, cta, "zh-hans", "subtitle", "请联系 SESCCO 讨论您的工程或承包需求。")
        set_loc(LocalizedContent, cta, "zh-hans", "button_text", "启动项目")


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0003_project_client_contractor_links"),
        ("core", "0004_sitesettings_footer_social_developer_credit"),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
