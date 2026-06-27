from django.db import migrations


def set_loc(LocalizedContent, obj, lang, field, text):
    if not obj or not getattr(obj, 'id', None):
        return
    LocalizedContent.objects.update_or_create(
        content_type=obj.__class__.__name__.lower(),
        object_id=obj.id,
        language_code=lang,
        field_name=field,
        defaults={"text": text},
    )


CLIENT_NAME_AR = {
    'Saudi Electricity Company': 'سعودي إلكتريسيتي كومباني',
    'Saudi Water Company': 'سعودي ووتر كومباني',
    'Energy & Power Contracting Co.': 'إنرجي آند باور كونتراكتنغ كو.',
    'Energy & Power Cont. Co.': 'إنرجي آند باور كونتراكتنغ كو.',
    'Energy & Power Cont. Co. Ltd.': 'إنرجي آند باور كونتراكتنغ كو. ليمتد',
    'Abahsain Consolidated Co.': 'أبهسين كونسوليديتد كو.',
    'Abhasain Consolidating Co.': 'أبهسين كونسوليديتنغ كو.',
    'Rommel Electro Arabia': 'روميل إلكترو أرابيا',
    'Future Technologies': 'فيوتشر تكنولوجيز',
    'SEPCO': 'سيبكو',
    'SINOMA': 'سينوما',
    'Havelock One': 'هافلوك ون',
    'Havelock1': 'هافلوك ون',
    'McDermott Arabia': 'ماكديرموت أرابيا',
    'Worley Parsons': 'وورلي بارسونز',
    'Roshan': 'روشن',
    'The Avenues Khobar': 'ذا أفنيوز الخبر',
    'ARAMCO': 'أرامكو',
    'Industrial Client': 'عميل صناعي',
    'SESCCO Team': 'فريق SESCCO',
    'EPC': 'EPC',
}

DURATION_AR = {
    '6 Months (June 2025)': '6 أشهر (يونيو 2025)',
    '7 Months (April 2026)': '7 أشهر (أبريل 2026)',
    '8 Months (April 2025)': '8 أشهر (أبريل 2025)',
    '8 Months (May 2025)': '8 أشهر (مايو 2025)',
    '6 Months (July 2025)': '6 أشهر (يوليو 2025)',
    'Completed May 2025': 'اكتمل في مايو 2025',
    '12 Months (Completed June 2023)': '12 شهراً (اكتمل في يونيو 2023)',
    '18 Months (Completed October 2024)': '18 شهراً (اكتمل في أكتوبر 2024)',
    'Starting 2025/2026': 'بدأ في 2025/2026',
    'Completed October 2016': 'اكتمل في أكتوبر 2016',
    'Completed August 2016': 'اكتمل في أغسطس 2016',
    'Project Completed': 'المشروع مكتمل',
}
DURATION_ZH = {
    '6 Months (June 2025)': '6 个月（2025 年 6 月）',
    '7 Months (April 2026)': '7 个月（2026 年 4 月）',
    '8 Months (April 2025)': '8 个月（2025 年 4 月）',
    '8 Months (May 2025)': '8 个月（2025 年 5 月）',
    '6 Months (July 2025)': '6 个月（2025 年 7 月）',
    'Completed May 2025': '2025 年 5 月完成',
    '12 Months (Completed June 2023)': '12 个月（2023 年 6 月完成）',
    '18 Months (Completed October 2024)': '18 个月（2024 年 10 月完成）',
    'Starting 2025/2026': '2025/2026 年开始',
    'Completed October 2016': '2016 年 10 月完成',
    'Completed August 2016': '2016 年 8 月完成',
    'Project Completed': '项目已完成',
}
LOCATION_AR = {
    'Saudi Arabia': 'المملكة العربية السعودية',
    'Yanbu, Saudi Arabia': 'ينبع، المملكة العربية السعودية',
    'Jubail, Saudi Arabia': 'الجبيل، المملكة العربية السعودية',
    'Jafurah, Saudi Arabia': 'الجافورة، المملكة العربية السعودية',
    'Riyadh, Saudi Arabia': 'الرياض، المملكة العربية السعودية',
    'Haradh, Saudi Arabia': 'حرض، المملكة العربية السعودية',
    'Al Khobar, Saudi Arabia': 'الخبر، المملكة العربية السعودية',
}
LOCATION_ZH = {
    'Saudi Arabia': '沙特阿拉伯',
    'Yanbu, Saudi Arabia': '延布，沙特阿拉伯',
    'Jubail, Saudi Arabia': '朱拜勒，沙特阿拉伯',
    'Jafurah, Saudi Arabia': '贾富拉，沙特阿拉伯',
    'Riyadh, Saudi Arabia': '利雅得，沙特阿拉伯',
    'Haradh, Saudi Arabia': '哈拉德，沙特阿拉伯',
    'Al Khobar, Saudi Arabia': '胡拜尔，沙特阿拉伯',
}


def forwards(apps, schema_editor):
    LocalizedContent = apps.get_model('core', 'LocalizedContent')
    Client = apps.get_model('clients', 'Client')
    Project = apps.get_model('projects', 'Project')
    ProjectMetric = apps.get_model('projects', 'ProjectMetric')
    ProjectCategory = apps.get_model('projects', 'ProjectCategory')
    DownloadDocument = apps.get_model('documents', 'DownloadDocument')
    DocumentCategory = apps.get_model('documents', 'DocumentCategory')
    DownloadsPageSettings = apps.get_model('documents', 'DownloadsPageSettings')
    CareerPageSettings = apps.get_model('careers', 'CareerPageSettings')

    for client in Client.objects.all():
        ar = CLIENT_NAME_AR.get(client.name, client.name)
        set_loc(LocalizedContent, client, 'ar', 'name', ar)
        set_loc(LocalizedContent, client, 'zh-hans', 'name', client.name)

    category_ar = {
        'Electrical Projects': 'المشاريع الكهربائية',
        'Civil Projects': 'المشاريع المدنية',
        'Architectural & Fitout Projects': 'مشاريع الأعمال المعمارية والتشطيبات',
        'Mechanical Projects': 'المشاريع الميكانيكية',
    }
    category_zh = {
        'Electrical Projects': '电气项目',
        'Civil Projects': '土建项目',
        'Architectural & Fitout Projects': '建筑与装修项目',
        'Mechanical Projects': '机械项目',
    }
    for cat in ProjectCategory.objects.all():
        if cat.name in category_ar:
            set_loc(LocalizedContent, cat, 'ar', 'name', category_ar[cat.name])
            set_loc(LocalizedContent, cat, 'zh-hans', 'name', category_zh[cat.name])

    # Correct seeded stakeholder data for the 13.8kV SWGR project based on the company profile table.
    try:
        ng_sec, _ = Client.objects.get_or_create(name='NG/SEC', defaults={'category': 'End Client', 'description': 'End client reference from project experience table.', 'is_featured': False})
        abahsain, _ = Client.objects.get_or_create(name='Abahsain Consolidated Co.', defaults={'category': 'Contractor', 'description': 'Contractor reference from project experience table.', 'is_featured': True})
        swgr = Project.objects.filter(title='Replacement of 13.8kV SWGR').first()
        if swgr:
            swgr.client = ng_sec
            swgr.contractor = abahsain
            swgr.client_name = 'NG/SEC'
            swgr.contractor_name = 'Abahsain Consolidated Co.'
            swgr.save(update_fields=['client', 'contractor', 'client_name', 'contractor_name'])
            set_loc(LocalizedContent, ng_sec, 'ar', 'name', 'NG/SEC')
            set_loc(LocalizedContent, ng_sec, 'zh-hans', 'name', 'NG/SEC')
            set_loc(LocalizedContent, abahsain, 'ar', 'name', CLIENT_NAME_AR['Abahsain Consolidated Co.'])
            set_loc(LocalizedContent, abahsain, 'zh-hans', 'name', 'Abahsain Consolidated Co.')
    except Exception:
        pass

    for project in Project.objects.all():
        if project.location in LOCATION_AR:
            set_loc(LocalizedContent, project, 'ar', 'location', LOCATION_AR[project.location])
            set_loc(LocalizedContent, project, 'zh-hans', 'location', LOCATION_ZH[project.location])
        if project.duration in DURATION_AR:
            set_loc(LocalizedContent, project, 'ar', 'duration', DURATION_AR[project.duration])
            set_loc(LocalizedContent, project, 'zh-hans', 'duration', DURATION_ZH[project.duration])

    label_ar = {'Location':'الموقع','Status':'الحالة','Duration':'المدة','Client':'العميل','Contractor':'المقاول','Year':'السنة','Category':'الفئة'}
    label_zh = {'Location':'地点','Status':'状态','Duration':'周期','Client':'客户','Contractor':'承包商','Year':'年份','Category':'类别'}
    status_ar = {'Completed':'مكتمل','Complete':'مكتمل','Ongoing':'قيد التنفيذ','Planned':'مخطط'}
    status_zh = {'Completed':'已完成','Complete':'已完成','Ongoing':'进行中','Planned':'计划中'}
    for metric in ProjectMetric.objects.all():
        if metric.label in label_ar:
            set_loc(LocalizedContent, metric, 'ar', 'label', label_ar[metric.label])
            set_loc(LocalizedContent, metric, 'zh-hans', 'label', label_zh[metric.label])
        if metric.value in DURATION_AR:
            set_loc(LocalizedContent, metric, 'ar', 'value', DURATION_AR[metric.value])
            set_loc(LocalizedContent, metric, 'zh-hans', 'value', DURATION_ZH[metric.value])
        elif metric.value in LOCATION_AR:
            set_loc(LocalizedContent, metric, 'ar', 'value', LOCATION_AR[metric.value])
            set_loc(LocalizedContent, metric, 'zh-hans', 'value', LOCATION_ZH[metric.value])
        elif metric.value in status_ar:
            set_loc(LocalizedContent, metric, 'ar', 'value', status_ar[metric.value])
            set_loc(LocalizedContent, metric, 'zh-hans', 'value', status_zh[metric.value])
        elif metric.value in CLIENT_NAME_AR:
            set_loc(LocalizedContent, metric, 'ar', 'value', CLIENT_NAME_AR[metric.value])
            set_loc(LocalizedContent, metric, 'zh-hans', 'value', metric.value)

    doc_ar = {
        'SESCCO Company Profile': ('ملف شركة SESCCO', 'ملف الشركة الرسمي باللغة الإنجليزية لشركة Summit Engineering Solutions Cont. Co. ويشمل رموز الموردين والقدرات والخدمات وخبرات المشاريع والشهادات.'),
        'ISO Certification Pack': ('حزمة شهادات ISO', 'مراجع شهادات الجودة والبيئة والصحة والسلامة المهنية.'),
        'Vendor Registration Information': ('معلومات تسجيل الموردين', 'معلومات مرجعية لرمز مورد أرامكو 10114560 ورمز مورد SEC 02013075.'),
    }
    doc_zh = {
        'SESCCO Company Profile': ('SESCCO 公司简介', 'Summit Engineering Solutions Cont. Co. 官方英文公司简介，包含供应商代码、能力、服务、项目经验和认证。'),
        'ISO Certification Pack': ('ISO 认证包', '质量、环境和职业健康安全认证资料。'),
        'Vendor Registration Information': ('供应商注册信息', 'Aramco 供应商代码 10114560 与 SEC 供应商代码 02013075 参考信息。'),
    }
    for doc in DownloadDocument.objects.all():
        if doc.title in doc_ar:
            set_loc(LocalizedContent, doc, 'ar', 'title', doc_ar[doc.title][0])
            set_loc(LocalizedContent, doc, 'ar', 'description', doc_ar[doc.title][1])
            set_loc(LocalizedContent, doc, 'zh-hans', 'title', doc_zh[doc.title][0])
            set_loc(LocalizedContent, doc, 'zh-hans', 'description', doc_zh[doc.title][1])
    for cat in DocumentCategory.objects.all():
        if cat.name == 'Company Documents':
            set_loc(LocalizedContent, cat, 'ar', 'name', 'مستندات الشركة')
            set_loc(LocalizedContent, cat, 'zh-hans', 'name', '公司文件')

    for settings in DownloadsPageSettings.objects.all():
        set_loc(LocalizedContent, settings, 'ar', 'hero_title', 'ملف الشركة والمستندات الرئيسية')
        set_loc(LocalizedContent, settings, 'ar', 'hero_subtitle', 'اطلع على ملف الشركة والشهادات والمعلومات الداعمة المهمة.')
        set_loc(LocalizedContent, settings, 'ar', 'intro_title', 'مركز المستندات')
        set_loc(LocalizedContent, settings, 'ar', 'intro_text', 'حمّل مستندات SESCCO أو اطلبها من مركز المستندات.')
        set_loc(LocalizedContent, settings, 'zh-hans', 'hero_title', '公司简介与关键文件')
        set_loc(LocalizedContent, settings, 'zh-hans', 'hero_subtitle', '查看公司简介、认证和重要支持信息。')
        set_loc(LocalizedContent, settings, 'zh-hans', 'intro_title', '文件中心')
        set_loc(LocalizedContent, settings, 'zh-hans', 'intro_text', '在文件中心下载或申请 SESCCO 文件。')

    for settings in CareerPageSettings.objects.all():
        set_loc(LocalizedContent, settings, 'ar', 'application_guide_text', 'استخدم ملفات PDF أو DOC أو DOCX فقط. سيتلقى المتقدمون المختارون تفاصيل المقابلة عبر البريد الإلكتروني.')
        set_loc(LocalizedContent, settings, 'zh-hans', 'application_guide_text', '仅使用 PDF、DOC 或 DOCX 文件。入围申请人将通过电子邮件收到面试详情。')


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_sitesettings_footer_social_developer_credit'),
        ('clients', '0001_initial'),
        ('projects', '0004_detail_localization_polish'),
        ('documents', '0001_initial'),
        ('careers', '0007_email_verification_and_application_flags'),
    ]
    operations = [migrations.RunPython(forwards, backwards)]
