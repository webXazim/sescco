from django.core.management.base import BaseCommand
from apps.core.models import CompanyProfile, NavigationMenu, FooterColumn, FooterLink, CTASettings, TrustMetric, ContactMethod, OfficeLocation, BusinessHour, LocalizedContent
from apps.pages.models import Page, PageSection, HomeHero, HomeAboutBlock, HomeSectionSettings, HomeHighlight, AboutPageSettings, MissionVisionItem, ValueItem, LeadershipMessage, TimelineItem, FAQ, WhyChooseItem
from apps.services.models import ServiceCategory, Service, ServiceListPageSettings, ServiceListProcessStep, ServiceListFAQ, ServiceKeyPoint, ServiceDeliverable, ServiceProcessStep, ServiceFeature, ServiceFAQ, ServiceCTA
from apps.projects.models import ProjectCategory, Project, ProjectListPageSettings, ProjectMetric, ProjectCTA, ProjectScopeItem
from apps.clients.models import TrustPageSettings, Client, Partner, Certificate, ClientCategory, CertificateCategory, Accreditation, Standard, ComplianceBlock
from apps.documents.models import DownloadsPageSettings, DownloadDocument, DocumentPageCTA, DocumentCategory
from apps.careers.models import CareerBenefit, CareerDepartment, CareerPageSettings, CareerProcessStep, CareerStat, JobOpening
from apps.inquiries.models import ContactPageSettings, InquirySubject


def set_loc(obj, lang, field, text):
    if not obj or not getattr(obj, 'id', None): return
    LocalizedContent.objects.update_or_create(content_type=obj.__class__.__name__.lower(), object_id=obj.id, language_code=lang, field_name=field, defaults={'text': text})

def many(obj, lang, data):
    for k,v in data.items(): set_loc(obj, lang, k, v)


def set_loc(obj, language_code, field_name, text):
    if not obj or not getattr(obj, "id", None):
        return
    LocalizedContent.objects.update_or_create(
        content_type=obj.__class__.__name__.lower(),
        object_id=obj.id,
        language_code=language_code,
        field_name=field_name,
        defaults={"text": text},
    )


def set_many(obj, lang, mapping):
    for field, value in mapping.items():
        set_loc(obj, lang, field, value)


def clean_old_demo_values():
    LocalizedContent.objects.filter(text__startswith="ترجمة:").delete()
    LocalizedContent.objects.filter(text__startswith="Translation:").delete()
    LocalizedContent.objects.filter(text__startswith="翻译:").delete()


class Command(BaseCommand):
    help = 'Seed Arabic and Chinese localization for the SESCCO production content.'
    def handle(self,*args,**opts):
        self.stdout.write(self.style.HTTP_INFO('Seeding SESCCO Arabic/Chinese localization...'))
        LocalizedContent.objects.filter(text__startswith='ترجمة:').delete(); LocalizedContent.objects.filter(text__startswith='Translation:').delete(); LocalizedContent.objects.filter(text__startswith='翻译:').delete()
        company=CompanyProfile.objects.first()
        if company:
            many(company,'ar',{'company_name':'شركة سميت للحلول الهندسية للمقاولات','short_name':'SESCCO','tagline':'حيث تلتقي الهندسة عالية الجودة بالخدمة الموثوقة.','description':'<p>تتخصص SESCCO في تقديم خدمات هندسية وإنشائية ودعم تعاقدي موثوقة في المملكة العربية السعودية.</p><p>نلتزم بتنفيذ المشاريع وفق معايير عالية من السلامة والكفاءة والجودة.</p>','address':'الدمام، المنطقة الشرقية، المملكة العربية السعودية','city':'الدمام','country':'المملكة العربية السعودية'})
            many(company,'zh-hans',{'company_name':'Summit 工程解决方案承包公司','short_name':'SESCCO','tagline':'高质量工程与可靠服务的结合。','description':'<p>SESCCO 在沙特阿拉伯提供可靠的工程、施工和合同支持服务。</p><p>我们致力于以高标准的安全、效率和质量交付项目。</p>','address':'沙特阿拉伯东部省达曼','city':'达曼','country':'沙特阿拉伯'})
        nav={'Home':('الرئيسية','首页'),'About Us':('من نحن','关于我们'),'Services':('الخدمات','服务'),'Projects':('المشاريع','项目'),'Clients':('العملاء','客户'),'Certificates':('الشهادات','认证'),'Downloads':('التحميلات','下载'),'Careers':('الوظائف','招聘'),'Open Jobs':('الوظائف المتاحة','开放职位'),'Contact HR':('تواصل مع الموارد البشرية','联系人力资源'),'Contact':('اتصل بنا','联系')}
        for item in NavigationMenu.objects.all():
            ar,zh=nav.get(item.title,(item.title,item.title)); set_loc(item,'ar','title',ar); set_loc(item,'zh-hans','title',zh)
        for col in FooterColumn.objects.all():
            ar,zh=nav.get(col.title,('روابط','链接')); set_loc(col,'ar','title',ar); set_loc(col,'zh-hans','title',zh)
        footer_title_map = {
            **nav,
            'Electrical Engineering': ('الهندسة الكهربائية', '电气工程'),
            'Civil & Fitout Works': ('الأعمال المدنية والتشطيبات', '土建与装修工程'),
            'Telecommunication Services': ('خدمات الاتصالات', '通信服务'),
            'Contract Support': ('الدعم التعاقدي', '合同支持'),
            'Privacy Policy': ('سياسة الخصوصية', '隐私政策'),
            'Terms & Conditions': ('الشروط والأحكام', '条款与条件'),
            'Quality & Safety': ('الجودة والسلامة', '质量与安全'),
            'Vendor Registration': ('تسجيل الموردين', '供应商注册'),
            'Capabilities': ('القدرات', '能力'),
        }
        for link in FooterLink.objects.all():
            ar, zh = footer_title_map.get(link.title, (f"رابط {link.sort_order or link.id}", f"链接 {link.sort_order or link.id}"))
            set_loc(link, 'ar', 'title', ar)
            set_loc(link, 'zh-hans', 'title', zh)
        cta=CTASettings.objects.first()
        if cta:
            many(cta,'ar',{'header_cta_text':'تواصل معنا','main_cta_title':'لنبنِ شيئاً عظيماً معاً','main_cta_subtitle':'تواصل معنا للاستفسارات أو التعاون أو الدعم، وسنعود إليك في أقرب وقت.','main_cta_button_text':'تواصل مع فريقنا'})
            many(cta,'zh-hans',{'header_cta_text':'联系我们','main_cta_title':'让我们一起创造卓越','main_cta_subtitle':'请联系我们进行项目咨询、合作或支持，我们会尽快回复。','main_cta_button_text':'联系我们的团队'})
        hero=HomeHero.objects.first()
        if hero:
            many(hero,'ar',{'title':'حيث تلتقي الهندسة عالية الجودة بالخدمة الموثوقة.','subtitle':'تقدم SESCCO حلولاً هندسية وإنشائية وتقنية متكاملة في المملكة العربية السعودية مع التركيز على السلامة والجودة والنزاهة.','primary_button_text':'خدماتنا','secondary_button_text':'مشاريعنا'})
            many(hero,'zh-hans',{'title':'高质量工程与可靠服务的结合。','subtitle':'SESCCO 在沙特阿拉伯提供综合工程、施工和技术解决方案，核心是安全、质量和诚信。','primary_button_text':'我们的服务','secondary_button_text':'查看项目'})
        ha=HomeAboutBlock.objects.first()
        if ha:
            many(ha,'ar',{'eyebrow':'عن SESCCO','title':'حلول هندسية مبنية على الثقة.','body':'<p>تتخصص SESCCO في خدمات الهندسة الكهربائية والأعمال المدنية والمعمارية والتشطيبات والدعم التعاقدي.</p><p>نبني علاقاتنا على الثقة والاحترام والالتزام بجودة التنفيذ.</p>','button_text':'اعرف المزيد عنا'})
            many(ha,'zh-hans',{'eyebrow':'关于 SESCCO','title':'建立在信任之上的工程解决方案。','body':'<p>SESCCO 专注于电气工程、土建与建筑装修、合同支持等可靠服务。</p><p>我们以信任、尊重和高质量交付建立合作关系。</p>','button_text':'了解更多'})
        hs=HomeSectionSettings.objects.first()
        if hs:
            many(hs,'ar',{'services_eyebrow':'خدماتنا','services_title':'قدرات هندسية متكاملة للمشاريع المتطلبة.','projects_eyebrow':'خبرات المشاريع','projects_title':'خبرة مثبتة في الأعمال الكهربائية والمدنية والتشطيبات.','clients_eyebrow':'عملاؤنا','certificates_eyebrow':'الشهادات والامتثال','why_choose_eyebrow':'لماذا تختار SESCCO','why_choose_title':'شريك موثوق للجودة والسلامة والتنفيذ.'})
            many(hs,'zh-hans',{'services_eyebrow':'我们的服务','services_title':'面向复杂项目的综合工程能力。','projects_eyebrow':'项目经验','projects_title':'在电气、土建和装修工程方面的成熟经验。','clients_eyebrow':'我们的客户','certificates_eyebrow':'认证与合规','why_choose_eyebrow':'为什么选择 SESCCO','why_choose_title':'质量、安全和执行力的可靠伙伴。'})

        # Upgrade 137: visible localization for Why Choose cards on the home/about pages.
        # These cards are CMS rows, not static template strings, so they must be localized row-by-row.
        why_choose_map = {
            'Safety-Focused Execution': {
                'ar': ('تنفيذ يركز على السلامة', 'نلتزم بممارسات عمل آمنة وتنفيذ موقعي موثوق في كل مرحلة.'),
                'zh-hans': ('以安全为核心的执行', '我们重视安全作业实践，并确保现场执行可靠有序。'),
            },
            'Skilled Workforce': {
                'ar': ('كوادر فنية مؤهلة', 'فريق مؤهل قادر على دعم متطلبات المشاريع المعقدة بكفاءة.'),
                'zh-hans': ('熟练专业团队', '合格人员能够高效支持复杂项目需求。'),
            },
            'Flexible Contract Support': {
                'ar': ('دعم تعاقدي مرن', 'دعم قابل للتوسع لفرق المشروع والمعدات وفق احتياجات كل مشروع.'),
                'zh-hans': ('灵活合同支持', '根据项目需求提供可扩展的项目团队与设备支持。'),
            },
            'Quality Commitment': {
                'ar': ('التزام بالجودة', 'عمل منظم يستند إلى الجودة والكفاءة ورضا العملاء.'),
                'zh-hans': ('质量承诺', '以质量、效率和客户满意度为导向开展工作。'),
            },
        }
        for item in WhyChooseItem.objects.all():
            payload = why_choose_map.get(item.title)
            if payload:
                ar_title, ar_desc = payload['ar']
                zh_title, zh_desc = payload['zh-hans']
                many(item, 'ar', {'title': ar_title, 'description': ar_desc})
                many(item, 'zh-hans', {'title': zh_title, 'description': zh_desc})

        home_page=Page.objects.filter(template_type='home').first()
        if home_page:
            many(home_page,'ar',{'title':'الرئيسية','hero_title':'حيث تلتقي الهندسة عالية الجودة بالخدمة الموثوقة.','hero_subtitle':'تقدم SESCCO حلولاً هندسية وإنشائية وتقنية متكاملة في المملكة العربية السعودية.','body':'<p>تعرف على خدمات SESCCO ومشاريعها وشهاداتها وقدراتها الهندسية.</p>','seo_title':'SESCCO | الهندسة عالية الجودة والخدمة الموثوقة','seo_description':'تقدم SESCCO خدمات الهندسة الكهربائية والأعمال المدنية والتشطيبات والدعم التعاقدي في المملكة العربية السعودية.'})
            many(home_page,'zh-hans',{'title':'首页','hero_title':'高质量工程与可靠服务的结合。','hero_subtitle':'SESCCO 在沙特阿拉伯提供综合工程、施工和技术解决方案。','body':'<p>了解 SESCCO 的服务、项目、认证和工程能力。</p>','seo_title':'SESCCO | 高质量工程与可靠服务','seo_description':'SESCCO 在沙特阿拉伯提供电气工程、土建工程、装修和合同支持服务。'})
        about=Page.objects.filter(template_type='about').first()
        if about:
            many(about,'ar',{'title':'من نحن','hero_title':'عن سميت للحلول الهندسية','hero_subtitle':'شركة مقاولات سعودية تقدم خدمات هندسية وإنشائية ودعم متكاملة.','body':'<p>نفخر في SESCCO بكوننا شريكاً موثوقاً في تحقيق أهداف المشاريع.</p><p>تشمل أنشطتنا الهندسة الكهربائية والأعمال المدنية والمعمارية والتشطيبات والأعمال الكهروميكانيكية والدعم التعاقدي.</p>','seo_title':'من نحن | SESCCO','seo_description':'تعرف على SESCCO وخدماتها الهندسية والإنشائية.'})
            many(about,'zh-hans',{'title':'关于我们','hero_title':'关于 Summit 工程解决方案','hero_subtitle':'一家位于沙特的承包公司，提供综合工程、施工和支持服务。','body':'<p>SESCCO 以成为客户实现项目目标的可靠伙伴而自豪。</p><p>我们的业务涵盖电气工程、土建与建筑装修、机电工程和合同支持服务。</p>','seo_title':'关于 SESCCO','seo_description':'了解 SESCCO 的工程和施工服务。'})
        aps=AboutPageSettings.objects.first()
        if aps:
            many(aps,'ar',{'overview_eyebrow':'نبذة عن الشركة','overview_title':'شريك هندسي ومقاولات موثوق.','mission_section_title':'الرسالة والرؤية والقيم','timeline_eyebrow':'رحلتنا','strengths_eyebrow':'نقاط قوتنا','strengths_title':'مصممون لتسليم المشاريع باعتمادية.'})
            many(aps,'zh-hans',{'overview_eyebrow':'公司概览','overview_title':'可靠的工程与承包伙伴。','mission_section_title':'使命、愿景与价值观','timeline_eyebrow':'我们的历程','strengths_eyebrow':'我们的优势','strengths_title':'为可靠项目交付而构建。'})

        # Upgrade 138: visible About-page localization for Mission/Vision/Values and Timeline cards.
        # These rows appear on /ar/about/ and were still falling back to English because
        # the original seed only translated AboutPageSettings, not the child CMS rows.
        mission_vision_map = {
            'Mission': (
                {'title': 'رسالتنا', 'description': 'تقديم حلول هندسية وإنشائية ودعم فني موثوقة من خلال تنفيذ آمن وجودة عمل منضبطة وإدارة عملية للمشاريع.'},
                {'title': '使命', 'description': '通过安全执行、规范工艺和务实项目管控，提供可靠的工程、施工和技术支持解决方案。'},
            ),
            'Vision': (
                {'title': 'رؤيتنا', 'description': 'أن نكون شريكاً هندسياً موثوقاً في المملكة العربية السعودية، معروفاً بالاعتمادية وجودة الأداء والقيمة طويلة الأمد للعملاء.'},
                {'title': '愿景', 'description': '成为沙特阿拉伯值得信赖的工程合作伙伴，以可靠性、优质表现和长期客户价值而被认可。'},
            ),
        }
        for item in MissionVisionItem.objects.all():
            payload = mission_vision_map.get(item.title)
            if payload:
                ar_map, zh_map = payload
                many(item, 'ar', ar_map)
                many(item, 'zh-hans', zh_map)

        value_map = {
            'Trust & Respect': (
                {'title': 'الثقة والاحترام', 'description': 'نلتزم بوعودنا ونتواصل بوضوح ونبني العلاقات على المسؤولية والاحتراف والاحترام.'},
                {'title': '信任与尊重', 'description': '我们信守承诺、清晰沟通，并以责任、专业和尊重建立合作关系。'},
            ),
            'Safe Workplace': (
                {'title': 'بيئة عمل آمنة', 'description': 'نحمي الأفراد والمواقع والبيئة من خلال ممارسات عمل آمنة وإشراف مسؤول.'},
                {'title': '安全工作环境', 'description': '通过安全作业实践和负责任的监督，保护人员、现场和环境。'},
            ),
            'Quality Execution': (
                {'title': 'تنفيذ عالي الجودة', 'description': 'نركز على التسليم الموثوق والتوثيق السليم وجودة العمل التي تلبي متطلبات المشروع.'},
                {'title': '高质量执行', 'description': '我们专注于可靠交付、规范文件和满足项目要求的施工质量。'},
            ),
        }
        for value in ValueItem.objects.all():
            payload = value_map.get(value.title)
            if payload:
                ar_map, zh_map = payload
                many(value, 'ar', ar_map)
                many(value, 'zh-hans', zh_map)

        timeline_map = {
            'Foundation': (
                {'title': 'التأسيس', 'description': 'تأسست SESCCO لتقديم خدمات هندسية ومقاولات موثوقة.'},
                {'title': '成立', 'description': 'SESCCO 成立，专注提供可靠的工程与承包服务。'},
            ),
            'Major Civil Works': (
                {'title': 'أعمال مدنية رئيسية', 'description': 'المشاركة في أعمال مدنية وصناعية وبنية تحتية.'},
                {'title': '主要土建工程', 'description': '参与工业土建和基础设施工程。'},
            ),
            'Pipeline Experience': (
                {'title': 'خبرة خطوط الأنابيب', 'description': 'دعم تنفيذ أعمال مسارات خطوط الأنابيب والحفر والردم والتسوية.'},
                {'title': '管线项目经验', 'description': '支持管线走廊、沟槽开挖、回填和整平等施工。'},
            ),
            'Expanded Project Portfolio': (
                {'title': 'توسع محفظة المشاريع', 'description': 'استمرار التنفيذ في المشاريع الكهربائية والمدنية والتشطيبات والدعم التعاقدي.'},
                {'title': '项目组合扩展', 'description': '持续交付电气、土建、装修和合同支持项目。'},
            ),
        }
        for item in TimelineItem.objects.all():
            payload = timeline_map.get(item.title)
            if payload:
                ar_map, zh_map = payload
                many(item, 'ar', ar_map)
                many(item, 'zh-hans', zh_map)

        leadership = LeadershipMessage.objects.filter(is_active=True).order_by('sort_order', 'id').first()
        if leadership:
            many(leadership,'ar',{
                'title':'كلمة اللجنة الإدارية',
                'message':'<p>في شركة سميت للحلول الهندسية للمقاولات، يقوم تقدمنا على التنفيذ المنضبط والمسؤولية الفنية والالتزام بالسلامة والجودة وثقة العملاء طويلة الأمد. نتعامل مع كل مشروع بدقة وهدف واضح لتقديم حلول هندسية تلبي أعلى المعايير وتخلق قيمة مستدامة لعملائنا وفرقنا والمجتمعات التي نخدمها.</p><p>الجودة في صميم كل ما نقوم به. فمن التخطيط الدقيق إلى التنفيذ المنظم، نلتزم بأنظمة قوية وأفضل الممارسات لضمان نتائج موثوقة وآمنة وفعالة.</p><p>وبصفتنا لجنة إدارية، نواصل تعزيز قدراتنا والاستثمار في كوادرنا وتقنياتنا وتقديم حلول تساهم في نمو المملكة ومستقبلها الصناعي المستدام.</p>',
                'person_name':'اللجنة الإدارية',
                'person_designation':'شركة سميت للحلول الهندسية للمقاولات'
            })
            many(leadership,'zh-hans',{
                'title':'管理委员会致辞',
                'message':'<p>在 Summit Engineering Solutions Cont. Co.，我们的进步建立在严谨执行、技术责任以及对安全、质量和长期客户信任的承诺之上。我们以精准和明确目标对待每一个项目，交付符合高标准并创造长期价值的工程解决方案。</p><p>质量是我们一切工作的核心。从严密规划到细致执行，我们坚持稳健体系和行业最佳实践，确保可靠、高效和安全的成果。</p><p>作为管理委员会，我们将继续强化能力、投资人才与技术，并交付有助于沙特王国可持续工业未来的解决方案。</p>',
                'person_name':'管理委员会',
                'person_designation':'Summit 工程解决方案承包公司'
            })
        slps=ServiceListPageSettings.objects.first()
        if slps:
            many(slps,'ar',{'eyebrow':'نظرة عامة على الخدمات','hero_title':'خدمات هندسية ومقاولات متكاملة','hero_subtitle':'من الأنظمة الكهربائية والأعمال المدنية إلى التشطيبات والدعم التعاقدي، تقدم SESCCO حلول مشاريع موثوقة.','intro_title':'خدمات عملية لتنفيذ موثوق.','intro_text':'<p>تم تصميم نموذج خدماتنا لدعم تنفيذ المشاريع بأمان وكفاءة وجودة عالية.</p>'})
            many(slps,'zh-hans',{'eyebrow':'服务概览','hero_title':'综合工程与承包服务','hero_subtitle':'从电气系统和土建工程到建筑装修和合同支持，SESCCO 提供可靠的项目解决方案。','intro_title':'面向可靠执行的实用服务。','intro_text':'<p>我们的服务模式旨在支持安全、高效和高质量项目交付。</p>'})
        service_ar={'Electrical Engineering Services':'خدمات الهندسة الكهربائية','Civil, Architectural & Fitout Works':'الأعمال المدنية والمعمارية والتشطيبات','Contract Support Service':'خدمات الدعم التعاقدي','Telecommunication Services':'خدمات الاتصالات','Electromechanical Works':'الأعمال الكهروميكانيكية','Mechanical & Fire-Fighting Systems':'الأنظمة الميكانيكية ومكافحة الحريق'}
        service_zh={'Electrical Engineering Services':'电气工程服务','Civil, Architectural & Fitout Works':'土建、建筑与装修工程','Contract Support Service':'合同支持服务','Telecommunication Services':'通信服务','Electromechanical Works':'机电工程','Mechanical & Fire-Fighting Systems':'机械与消防系统'}
        for s in Service.objects.all():
            ar=service_ar.get(s.title,s.title); zh=service_zh.get(s.title,s.title)
            many(s,'ar',{'title':ar,'short_description':'خدمة موثوقة تدعم تنفيذ المشاريع بأمان وكفاءة وجودة.','body':'<p>تقدم SESCCO هذه الخدمة من خلال كوادر مؤهلة وإجراءات منظمة لضمان جودة التنفيذ وسلامته.</p>','seo_title':f'{ar} | SESCCO','seo_description':'خدمة من SESCCO لدعم المشاريع في المملكة العربية السعودية.'})
            many(s,'zh-hans',{'title':zh,'short_description':'支持项目安全、高效和高质量执行的可靠服务。','body':'<p>SESCCO 通过合格团队和规范流程提供该服务，确保执行质量与安全。</p>','seo_title':f'{zh} | SESCCO','seo_description':'SESCCO 在沙特阿拉伯支持项目的服务。'})
        for cat in ServiceCategory.objects.all():
            map_ar={'Electrical Engineering':'الهندسة الكهربائية','Civil & Architectural Fitout':'الأعمال المدنية والمعمارية والتشطيبات','Contract Support':'الدعم التعاقدي','Telecommunication Services':'خدمات الاتصالات','Electromechanical Works':'الأعمال الكهروميكانيكية','Mechanical & Fire Fighting':'الميكانيكا ومكافحة الحريق'}; map_zh={'Electrical Engineering':'电气工程','Civil & Architectural Fitout':'土建与建筑装修','Contract Support':'合同支持','Telecommunication Services':'通信服务','Electromechanical Works':'机电工程','Mechanical & Fire Fighting':'机械与消防'}
            many(cat,'ar',{'name':map_ar.get(cat.name,cat.name),'description':'تصنيف لخدمات SESCCO المتخصصة.'}); many(cat,'zh-hans',{'name':map_zh.get(cat.name,cat.name),'description':'SESCCO 专业服务类别。'})
        for qs, ardata, zhdata in [(ServiceKeyPoint.objects.all(), {'title':'نقطة رئيسية','description':'عنصر أساسي ضمن نطاق الخدمة.'},{'title':'关键点','description':'服务范围内的核心内容。'}),(ServiceDeliverable.objects.all(), {'title':'مخرج الخدمة','description':'مخرج واضح يدعم متطلبات المشروع.'},{'title':'服务交付内容','description':'支持项目要求的明确交付内容。'}),(ServiceProcessStep.objects.all(), {'title':'خطوة التنفيذ','description':'مرحلة منظمة ضمن عملية التنفيذ.'},{'title':'执行步骤','description':'执行流程中的有序阶段。'}),(ServiceListProcessStep.objects.all(), {'title':'خطوة تنفيذ','description':'مرحلة منظمة ضمن طريقة عمل SESCCO.'},{'title':'执行步骤','description':'SESCCO 工作方法中的有序阶段。'}),(ServiceFeature.objects.all(), {'title':'ميزة الخدمة','description':'ميزة عملية تدعم السلامة والجودة والتنفيذ.'},{'title':'服务特点','description':'支持安全、质量和执行的实际特点。'}),(ServiceCTA.objects.all(), {'title':'هل تحتاج إلى دعم لهذا العمل؟','subtitle':'تواصل مع SESCCO لمناقشة متطلبات مشروعك.','button_text':'اطلب عرضاً'},{'title':'需要该项支持？','subtitle':'联系 SESCCO 讨论您的项目需求。','button_text':'申请报价'})]:
            for obj in qs: many(obj,'ar',ardata); many(obj,'zh-hans',zhdata)
        for faq in ServiceFAQ.objects.all():
            many(faq,'ar',{'question':'سؤال شائع حول الخدمة','answer':'<p>يمكن لفريق SESCCO توضيح نطاق الخدمة ومتطلبات التنفيذ بعد مراجعة تفاصيل المشروع.</p>'})
            many(faq,'zh-hans',{'question':'关于该服务的常见问题','answer':'<p>SESCCO 团队可在审核项目详情后说明服务范围和执行要求。</p>'})
        for faq in ServiceListFAQ.objects.all():
            many(faq,'ar',{'question':'سؤال شائع حول خدمات SESCCO','answer':'<p>تقدم SESCCO خدمات هندسية ومقاولات ودعم مشاريع وفق متطلبات العميل والموقع.</p>'})
            many(faq,'zh-hans',{'question':'关于 SESCCO 服务的常见问题','answer':'<p>SESCCO 根据客户和现场要求提供工程、承包和项目支持服务。</p>'})
        plps=ProjectListPageSettings.objects.first()
        if plps:
            many(plps,'ar',{'eyebrow':'خبرات المشاريع','hero_title':'خبرة مشاريع مثبتة في المملكة العربية السعودية','hero_subtitle':'تشمل محفظة SESCCO مشاريع كهربائية واتصالات ومدنية ومعمارية وتشطيبات وأنابيب وميكانيكا ودعم.','intro_title':'خبرة تعكس قدرة التنفيذ.','intro_text':'<p>تُظهر خبراتنا القدرة على العمل في بيئات صناعية وخدمية وتجارية معقدة.</p>'})
            many(plps,'zh-hans',{'eyebrow':'项目经验','hero_title':'在沙特阿拉伯的成熟项目经验','hero_subtitle':'SESCCO 的项目组合涵盖电气、通信、土建、建筑装修、管道、机械和支持项目。','intro_title':'体现执行能力的经验。','intro_text':'<p>我们的项目经验展示了在复杂环境中工作的能力。</p>'})
        project_ar={'Replacement of Existing Outdoor Aindar Sub-30 with New GIS Substation':'استبدال محطة عين دار الخارجية بمحطة GIS جديدة','Yanbu 4 - 110kV HV Substation Interface Works':'أعمال الربط لمحطة ينبع 4 جهد 110 ك.ف','Replacement of 13.8kV SWGR':'استبدال لوحة مفاتيح جهد 13.8 ك.ف','MV Cable Fault Location Test, Damage Repair and Termination':'اختبار تحديد عطل كابل الجهد المتوسط وإصلاحه وإنهاؤه','EPCC 10,000TPD Clinker Cement Plant Civil Works':'الأعمال المدنية لمشروع مصنع كلنكر أسمنت بطاقة 10,000 طن يومياً','EPCC 10,000TPD Clinker Cement Plant Architectural & Fitout Works':'الأعمال المعمارية والتشطيبات لمشروع مصنع الكلنكر','Roshan Ewan Sedra 2 Villas Tile Works':'أعمال البلاط لفلل روشن إيوان سدرة 2','Haradh RTR Pipeline Project':'مشروع خط أنابيب هرض RTR','Jafurah Upstream Pipeline Project':'مشروع خط أنابيب الجافورة','The Avenues Khobar Plaster and Screed Works':'أعمال اللياسة والسكريد في ذا أفنيوز الخبر','McDermott Arabia Office Fitout':'تشطيبات مكتب ماكديرموت العربية','Worley Parsons Office Fitout':'تشطيبات مكتب وورلي بارسونز','Fire-Fighting System Installation for Industrial Facility and Warehouse':'تركيب نظام مكافحة الحريق لمنشأة صناعية ومستودع'}
        project_zh={'Replacement of Existing Outdoor Aindar Sub-30 with New GIS Substation':'Aindar 室外 Sub-30 更换为新 GIS 变电站','Yanbu 4 - 110kV HV Substation Interface Works':'Yanbu 4 110kV 高压变电站接口工程','Replacement of 13.8kV SWGR':'13.8kV 开关柜更换工程','MV Cable Fault Location Test, Damage Repair and Termination':'中压电缆故障定位、损伤修复与终端施工','EPCC 10,000TPD Clinker Cement Plant Civil Works':'日产 10,000 吨熟料水泥厂土建工程','EPCC 10,000TPD Clinker Cement Plant Architectural & Fitout Works':'日产 10,000 吨熟料水泥厂建筑与装修工程','Roshan Ewan Sedra 2 Villas Tile Works':'Roshan Ewan Sedra 2 别墅瓷砖工程','Haradh RTR Pipeline Project':'Haradh RTR 管道项目','Jafurah Upstream Pipeline Project':'Jafurah 上游管道项目','The Avenues Khobar Plaster and Screed Works':'The Avenues Khobar 抹灰与找平层工程','McDermott Arabia Office Fitout':'McDermott Arabia 办公室装修工程','Worley Parsons Office Fitout':'Worley Parsons 办公室装修工程','Fire-Fighting System Installation for Industrial Facility and Warehouse':'工业设施与仓库消防系统安装工程'}
        for pr in Project.objects.all():
            ar=project_ar.get(pr.title, f'مشروع {pr.title}'); zh=project_zh.get(pr.title, f'{pr.title} 项目')
            many(pr,'ar',{'title':ar,'short_description':'مشروع يعكس قدرة SESCCO على التنفيذ الآمن والموثوق.','summary':'<p>يعكس هذا المشروع خبرة SESCCO في التخطيط والتنفيذ وتسليم الأعمال وفق متطلبات العميل.</p>','challenge':'<p>تطلب المشروع تنسيقاً فنياً وتشغيلياً لضمان التنفيذ الآمن والجيد.</p>','scope':'<p>شمل نطاق العمل التنفيذ والمتابعة الفنية حسب طبيعة المشروع.</p>','solution':'<p>قدمت SESCCO دعماً عملياً من خلال كوادر مؤهلة وتنفيذ منظم.</p>','outcomes':'<p>ساهم المشروع في تحقيق أهداف العميل مع الالتزام بالجودة والسلامة.</p>','seo_title':f'{ar} | خبرات SESCCO','seo_description':'دراسة حالة ضمن خبرات SESCCO في المشاريع.'})
            many(pr,'zh-hans',{'title':zh,'short_description':'体现 SESCCO 安全可靠执行能力的项目。','summary':'<p>该项目体现了 SESCCO 在规划、执行和交付方面的经验。</p>','challenge':'<p>项目需要技术和运营协调，以确保安全和高质量执行。</p>','scope':'<p>工作范围包括执行和技术跟进。</p>','solution':'<p>SESCCO 通过合格团队和有序执行提供实用支持。</p>','outcomes':'<p>项目在质量和安全承诺下支持了客户目标。</p>','seo_title':f'{zh} | SESCCO 项目经验','seo_description':'SESCCO 项目经验案例。'})
        tps=TrustPageSettings.objects.first()
        if tps:
            many(tps,'ar',{'eyebrow':'الشهادات والعملاء','hero_title':'الشهادات والعملاء.','hero_subtitle':'راجع شهادات SESCCO أولاً، ثم الجهات العميلة المرتبطة بخبراتنا في المشاريع.','clients_eyebrow':'عملاؤنا الرئيسيون','clients_title':'موثوقون من قبل منظمات محترمة.','partners_eyebrow':'شبكة المشاريع','partners_title':'المقاولون مخصصون فقط لسجلات تفاصيل المشاريع.','certificates_eyebrow':'شهاداتنا','certificates_title':'أنظمة معتمدة وتميز تشغيلي.','standards_eyebrow':'الامتثال والمعايير','standards_title':'المعايير التي توجه عملنا.'})
            many(tps,'zh-hans',{'eyebrow':'认证与客户','hero_title':'认证与客户。','hero_subtitle':'先查看 SESCCO 的认证，然后查看与项目经验相关的客户单位。','clients_eyebrow':'主要客户','clients_title':'受到知名组织的信赖。','partners_eyebrow':'项目网络','partners_title':'承包商仅用于项目详情记录。','certificates_eyebrow':'我们的认证','certificates_title':'认证体系与运营卓越。','standards_eyebrow':'合规与标准','standards_title':'指导我们工作的标准。'})
        client_name_ar = {

            'Abahsain Consolidating Co.': 'أبهسين كونسوليديتنغ كو.',
            'Al Rajhi Bank': 'الراجحي بنك',
            'ABRAR': 'أبرار',
            'DACO': 'داكو',
            'BCC': 'بي سي سي',
            'MOBILY': 'موبايلي',
            'McDermott': 'ماكديرموت',
            'L & T': 'إل آند تي',
            'Riyadh Airport Company': 'رياض إيربورت كومباني',
            'Novartis': 'نوفارتس',
            'NHC': 'إن إتش سي',
            'Royal Comision': 'رويال كومشن',
            'SABIC': 'سابك',
            'SAIPEM': 'سايبم',
            'Saudi Energy': 'سعودي إنرجي',
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
            'SEC': 'إس إي سي',
            'STC': 'إس تي سي',
            'TR': 'تي آر',
            'Saudi National Bank': 'سعودي ناشونال بنك',
            'Seven Entertainment Ventures': 'سفن إنترتينمنت فينتشرز',
            'ZAIN': 'زين',
        }
        for client in Client.objects.all():
            many(client,'ar',{'name':client_name_ar.get(client.name, client.name),'category':'عميل / جهة مشروع','description':'من الجهات المرتبطة بخبرات SESCCO في المشاريع.'})
            many(client,'zh-hans',{'name':client.name,'category':'客户 / 项目相关方','description':'与 SESCCO 项目经验相关的组织之一。'})
        project_category_names = {
            'Telecommunication Projects': ('مشاريع الاتصالات', '通信项目'),
        }
        for category in ProjectCategory.objects.all():
            localized_names = project_category_names.get(category.name)
            if localized_names:
                many(category, 'ar', {'name': localized_names[0]})
                many(category, 'zh-hans', {'name': localized_names[1]})
        for method in ContactMethod.objects.all():
            ar={'Call Us':'اتصل بنا','WhatsApp':'واتساب','Email Us':'راسلنا عبر البريد'}.get(method.title,method.title); zh={'Call Us':'致电我们','WhatsApp':'WhatsApp','Email Us':'邮件联系'}.get(method.title,method.title)
            many(method,'ar',{'title':ar,'value':method.value}); many(method,'zh-hans',{'title':zh,'value':method.value})
        cps=ContactPageSettings.objects.first()
        if cps:
            many(cps,'ar',{'eyebrow':'اتصل بنا','hero_title':'تواصل مع SESCCO بثقة.','hero_subtitle':'أرسل متطلباتك أو اعرض موقعنا أو تواصل مع الفريق المناسب من صفحة اتصال واضحة ومنظمة.','intro_title':'ابدأ استفسار مشروعك بوضوح.','intro_text':'استخدم النموذج لمشاركة متطلبات مشروعك. تم فصل طرق التواصل والخريطة ومعلومات المكتب حتى لا يرى الزائر محتوى مكرراً.','map_eyebrow':'موقعنا','map_title':'اعثر على SESCCO في خرائط Google.','map_subtitle':'استخدم عرض الخريطة الكبير لتحديد موقع المكتب وفتح الاتجاهات مباشرة في خرائط Google.','map_button_text':'فتح في خرائط Google'})
            many(cps,'zh-hans',{'eyebrow':'联系我们','hero_title':'放心联系 SESCCO。','hero_subtitle':'通过清晰的联系页面提交需求、查看位置或联系合适团队。','intro_title':'清晰提交您的项目咨询。','intro_text':'使用表单分享您的项目需求。联系方式、地图和办公室信息分开展示，避免访客看到重复内容。','map_eyebrow':'找到我们','map_title':'在 Google 地图中查找 SESCCO。','map_subtitle':'使用大型地图查看办公室位置，并直接在 Google 地图中打开路线。','map_button_text':'在 Google 地图中打开'})
        for office in OfficeLocation.objects.all(): many(office,'ar',{'name':'المكتب الرئيسي','address':'الدمام، المنطقة الشرقية، المملكة العربية السعودية','city':'الدمام','country':'المملكة العربية السعودية'}); many(office,'zh-hans',{'name':'总部办公室','address':'沙特阿拉伯东部省达曼','city':'达曼','country':'沙特阿拉伯'})
        for hour in BusinessHour.objects.all():
            if hour.day_label == 'Friday':
                many(hour,'ar',{'day_label':'الجمعة','hours':'مغلق'}); many(hour,'zh-hans',{'day_label':'周五','hours':'休息'})
            elif 'Saturday' in hour.day_label:
                many(hour,'ar',{'day_label':'السبت - الخميس','hours':'8:00 صباحاً - 5:00 مساءً'}); many(hour,'zh-hans',{'day_label':'周六至周四','hours':'上午 8:00 - 下午 5:00'})
            else:
                many(hour,'ar',{'day_label':'الأحد - الخميس','hours':'8:00 صباحاً - 5:00 مساءً'}); many(hour,'zh-hans',{'day_label':'周日至周四','hours':'上午 8:00 - 下午 5:00'})
        for subj in InquirySubject.objects.all():
            ar={'General Inquiry':'استفسار عام','Project Quotation':'طلب عرض سعر','Document Request':'طلب مستند','Contract Support':'دعم تعاقدي','Partnership':'شراكة'}.get(subj.title,subj.title); zh={'General Inquiry':'一般咨询','Project Quotation':'项目报价','Document Request':'文件申请','Contract Support':'合同支持','Partnership':'合作'}.get(subj.title,subj.title); set_loc(subj,'ar','title',ar); set_loc(subj,'zh-hans','title',zh)
        for metric in TrustMetric.objects.all():
            m={'Saudi Arabia Based':('في السعودية','الدمام، السعودية','位于沙特','达曼，沙特'),'Established':('تأسست','2015','成立于','2015'),'SEC Vendor Code':('رمز مورد SEC','02013075','SEC 供应商代码','02013075'),'Aramco Vendor Code':('رمز أرامكو','10114560','阿美代码','10114560'),'Trusted Clients':('عملاء موثوقون','85+','可信客户','85+'),'Certifications':('الشهادات','6+','认证','6+')}.get(metric.title)
            if m: ar_t,ar_v,zh_t,zh_v=m; many(metric,'ar',{'title':ar_t,'value':ar_v,'description':'مؤشر يعكس خبرة SESCCO والتزامها.'}); many(metric,'zh-hans',{'title':zh_t,'value':zh_v,'description':'体现 SESCCO 经验和承诺的指标。'})
        dps=DownloadsPageSettings.objects.first()
        if dps:
            many(dps,'ar',{'eyebrow':'التحميلات','hero_title':'ملف الشركة والمستندات الرئيسية','hero_subtitle':'يمكنك الوصول إلى ملف الشركة والشهادات والمعلومات الداعمة المهمة.','intro_title':'مركز المستندات','intro_text':'قم بتحميل أو طلب مستندات SESCCO من مركز المستندات.'})
            many(dps,'zh-hans',{'eyebrow':'下载','hero_title':'公司简介与关键文件','hero_subtitle':'访问公司简介、认证和重要支持信息。','intro_title':'文件中心','intro_text':'从文件中心下载或申请 SESCCO 文件。'})

        cpset=CareerPageSettings.objects.first()
        if cpset:
            many(cpset,'ar',{'eyebrow':'الوظائف','hero_title':'ابنِ مسارك المهني مع SESCCO','hero_subtitle':'استكشف الوظائف المتاحة، وقدّم عبر الإنترنت وانضم إلى فريق يلتزم بالتنفيذ الهندسي الآمن والموثوق.','hero_primary_button_text':'عرض الوظائف المتاحة','hero_secondary_button_text':'تواصل مع الموارد البشرية','meta_title':'الوظائف | SESCCO','meta_description':'استكشف فرص العمل في SESCCO وقدّم طلبك عبر الإنترنت مع السيرة الذاتية والمستندات الداعمة.','intro_eyebrow':'الفرص المتاحة','intro_title':'اعثر على الدور المناسب لخطوتك التالية','intro_text':'نراجع كل طلب بعناية وندعو المرشحين المختارين للمقابلة عبر البريد الإلكتروني الرسمي.','empty_jobs_title':'لا توجد وظائف مطابقة','empty_jobs_text':'جرّب بحثاً آخر أو راجع الصفحة لاحقاً لمعرفة الفرص الجديدة.','benefits_eyebrow':'لماذا تعمل معنا','benefits_title':'بيئة عملية للمهنيين الجادين','benefits_text':'تركز فرص SESCCO على الجاهزية للمشاريع والتنفيذ الآمن والنمو الفني والعمل الجماعي الموثوق.','process_eyebrow':'عملية التوظيف','process_title':'عملية توظيف بسيطة','process_text':'قدّم طلبك، تتم مراجعته، احضر المقابلة ثم انضم إلى فريق المشروع.','form_help_title':'قبل الإرسال','form_help_text':'جهّز سيرة ذاتية واضحة وأرفق المستندات التي تدعم الوظيفة. تأكد من صحة بريدك ورقم هاتفك.','application_guide_title':'قائمة التقديم','application_guide_text':'يفضل استخدام ملفات PDF أو DOCX. سيتلقى المرشحون المختارون تفاصيل المقابلة عبر البريد الإلكتروني.','applicant_profile_title':'ملف المتقدم','applicant_profile_text':'أضف موقعك وتصريح العمل والخبرة وروابط الملف الشخصي حتى يتمكن فريق الموارد البشرية من مراجعة الطلب بسرعة.','document_upload_title':'مستندات التقديم','document_upload_text':'ارفع السيرة الذاتية وأي شهادات أو تراخيص أو مستندات داعمة. يدعم النظام رفع عدة مستندات إضافية.','duplicate_application_title':'تم إرسال طلب سابقاً','duplicate_application_text':'لقد قدمت بالفعل على هذه الوظيفة باستخدام هذا البريد الإلكتروني. يرجى التواصل مع الموارد البشرية إذا كنت تحتاج إلى تحديث طلبك.','privacy_notice':'سيتم استخدام بياناتك فقط لمراجعة التوظيف والتواصل الرسمي بخصوص هذا الطلب.','success_eyebrow':'تم إرسال الطلب','success_title':'شكراً لتقديمك.','success_text':'تم استلام طلبك. سيقوم فريق الموارد البشرية بمراجعة سيرتك الذاتية ومستنداتك، وسيتم إرسال دعوة مقابلة للمرشحين المختارين عبر البريد الإلكتروني.','cta_title':'لم تجد الوظيفة المناسبة؟','cta_text':'راجع هذه الصفحة قريباً أو تواصل مع فريق الموارد البشرية للفرص المستقبلية.','cta_button_text':'تواصل مع الموارد البشرية','email_from_name':'فريق الموارد البشرية في SESCCO','email_verification_subject':'تحقق من بريدك الإلكتروني لطلب التوظيف','email_verification_body':'عزيزي المتقدم،\n\nاستخدم رمز التحقق التالي لإكمال طلب التوظيف لدى SESCCO:\n\n{{ code }}\n\nالوظيفة: {{ job.title }}\nينتهي هذا الرمز خلال {{ expiry_minutes }} دقيقة.\n\nإذا لم تطلب هذا الرمز، يمكنك تجاهل هذه الرسالة.\n\nمع التحية،\nفريق الموارد البشرية في SESCCO','interview_email_subject':'دعوة مقابلة — {{ job.title }}','interview_email_body':'عزيزي/عزيزتي {{ application.full_name }},\n\nشكراً لتقديمك على وظيفة {{ job.title }} في SESCCO.\n\nتم اختيارك لحضور مقابلة.\n\nرقم الطلب: {{ application.application_reference }}\n\nتفاصيل المقابلة:\nالوظيفة: {{ job.title }}\nالتاريخ والوقت: {{ application.interview_date|date:"l, F d, Y - h:i A" }}\nالنوع: {{ application.get_interview_mode_display }}\nالموقع / الرابط: {{ application.interview_location }}\n{% if application.interview_notes %}\nملاحظات إضافية:\n{{ application.interview_notes }}\n{% endif %}\nيرجى تجهيز السيرة الذاتية والهوية والشهادات ذات الصلة.\n\nمع التحية،\nفريق الموارد البشرية في SESCCO','rejection_email_subject':'تحديث بخصوص طلبك — {{ job.title }}','rejection_email_body':'عزيزي/عزيزتي {{ application.full_name }},\n\nشكراً لتقديمك على وظيفة {{ job.title }} في SESCCO.\n\nبعد مراجعة طلبك بعناية، لا يمكننا المتابعة بملفك لهذه الوظيفة في الوقت الحالي.\n\nرقم الطلب: {{ application.application_reference }}\n\n{% if rejection_reason %}ملاحظة من الموارد البشرية:\n{{ rejection_reason }}\n{% endif %}\nنقدر اهتمامك بـ SESCCO ونتمنى لك التوفيق.\n\nمع التحية،\nفريق الموارد البشرية في SESCCO'})
            many(cpset,'zh-hans',{'eyebrow':'招聘','hero_title':'与 SESCCO 一起发展职业生涯','hero_subtitle':'探索开放职位，在线申请，并加入致力于安全可靠工程执行的团队。','hero_primary_button_text':'查看开放职位','hero_secondary_button_text':'联系人力资源','meta_title':'招聘 | SESCCO','meta_description':'探索 SESCCO 职业机会，并在线提交简历和支持文件。','intro_eyebrow':'开放机会','intro_title':'找到适合您下一步的职位','intro_text':'我们认真审核每份申请，并通过官方电子邮件邀请入围候选人参加面试。','empty_jobs_title':'没有找到开放职位','empty_jobs_text':'请尝试其他搜索，或稍后查看新的机会。','benefits_eyebrow':'为什么加入我们','benefits_title':'适合专业人士的务实环境','benefits_text':'SESCCO 的职业机会围绕项目准备、安全执行、技术成长和可靠团队合作。','process_eyebrow':'招聘流程','process_title':'简单的招聘流程','process_text':'申请、审核、参加面试并加入项目团队。','form_help_title':'提交前','form_help_text':'请准备清晰的简历，并附上支持该职位的文件。确保电子邮件和电话号码正确。','application_guide_title':'申请清单','application_guide_text':'建议使用 PDF 或 DOCX 文件。入围申请人将通过电子邮件收到面试详情。','applicant_profile_title':'申请人资料','applicant_profile_text':'请添加您的所在地、工作许可、经验和个人资料链接，以便人力资源更快审核。','document_upload_title':'申请文件','document_upload_text':'上传简历以及相关证书、执照或项目支持文件。系统支持多个附加文件。','duplicate_application_title':'申请已提交','duplicate_application_text':'您已使用此电子邮件申请过该职位。如需更新申请，请联系人力资源。','privacy_notice':'您的信息仅用于招聘审核和有关此申请的正式沟通。','success_eyebrow':'申请已提交','success_title':'感谢您的申请。','success_text':'您的申请已收到。人力资源团队将审核您的简历和文件，入围者将通过电子邮件收到面试邀请。','cta_title':'没有找到合适职位？','cta_text':'请稍后再次查看本页面，或联系人力资源团队了解未来机会。','cta_button_text':'联系人力资源','email_from_name':'SESCCO 人力资源团队','email_verification_subject':'验证您的 SESCCO 职位申请邮箱','email_verification_body':'尊敬的申请人：\n\n请使用以下验证码继续您的 SESCCO 职位申请：\n\n{{ code }}\n\n职位：{{ job.title }}\n此验证码将在 {{ expiry_minutes }} 分钟后过期。\n\n如果您未请求此验证码，请忽略此邮件。\n\n此致，\nSESCCO 人力资源团队','interview_email_subject':'面试邀请 — {{ job.title }}','interview_email_body':'尊敬的 {{ application.full_name }}：\n\n感谢您申请 SESCCO 的 {{ job.title }} 职位。\n\n您已入围面试。\n\n申请编号：{{ application.application_reference }}\n\n面试详情：\n职位：{{ job.title }}\n日期和时间：{{ application.interview_date|date:"l, F d, Y - h:i A" }}\n方式：{{ application.get_interview_mode_display }}\n地点 / 会议链接：{{ application.interview_location }}\n{% if application.interview_notes %}\n补充说明：\n{{ application.interview_notes }}\n{% endif %}\n请准备好简历、身份证明和相关证书。\n\n此致，\nSESCCO 人力资源团队','rejection_email_subject':'申请进展更新 — {{ job.title }}','rejection_email_body':'尊敬的 {{ application.full_name }}：\n\n感谢您申请 SESCCO 的 {{ job.title }} 职位。\n\n经过认真审核，我们目前无法继续推进您此职位的申请。\n\n申请编号：{{ application.application_reference }}\n\n{% if rejection_reason %}人力资源备注：\n{{ rejection_reason }}\n{% endif %}\n感谢您对 SESCCO 的关注，欢迎未来申请合适机会。\n\n此致，\nSESCCO 人力资源团队'})
        for stat in CareerStat.objects.all():
            stat_ar={'Active departments':('الأقسام المتاحة','الهندسة والسلامة والجودة والإدارة.'),'Online application':('تقديم إلكتروني','يمكن للمتقدمين إرسال السير الذاتية والمستندات من صفحة الوظيفة.'),'Interview invite':('دعوة المقابلة','يتلقى المرشحون المختارون تفاصيل الدعوة الرسمية عبر البريد الإلكتروني.')}.get(stat.label)
            stat_zh={'Active departments':('开放部门','工程、安全质量和行政机会。'),'Online application':('在线申请','申请人可直接从职位页面提交简历和文件。'),'Interview invite':('面试邀请','入围申请人将通过电子邮件收到正式邀请详情。')}.get(stat.label)
            if stat_ar: many(stat,'ar',{'label':stat_ar[0],'description':stat_ar[1]})
            if stat_zh: many(stat,'zh-hans',{'label':stat_zh[0],'description':stat_zh[1]})
        benefit_map = {
            'Project-ready environment': ({'title':'بيئة جاهزة للمشاريع','description':'اعمل مع فرق تركز على التنفيذ العملي والتنسيق والتسليم الموثوق.'}, {'title':'项目就绪环境','description':'与专注于实际执行、协调和可靠交付的团队合作。'}),
            'Safety and quality focus': ({'title':'تركيز على السلامة والجودة','description':'ابنِ مسارك المهني في مكان عمل يحترم ممارسات السلامة ومعايير الجودة.'}, {'title':'重视安全与质量','description':'在尊重安全工作实践和质量标准的环境中发展职业生涯。'}),
            'Clear review workflow': ({'title':'آلية مراجعة واضحة','description':'تتم إدارة الطلبات والمستندات ودعوات المقابلة من خلال عملية إدارية منظمة.'}, {'title':'清晰的审核流程','description':'申请、文件和面试邀请通过结构化后台流程管理。'}),
        }
        for benefit in CareerBenefit.objects.all():
            values = benefit_map.get(benefit.title)
            if values:
                ar_map, zh_map = values; many(benefit,'ar',ar_map); many(benefit,'zh-hans',zh_map)
        process_map = {
            'Apply Online': ({'title':'التقديم عبر الإنترنت','description':'أرسل سيرتك الذاتية والمستندات الداعمة من صفحة الوظيفة.'}, {'title':'在线申请','description':'通过职位页面提交简历和支持文件。'}),
            'Admin Review': ({'title':'مراجعة الإدارة','description':'يراجع فريق الموارد البشرية الطلبات والمستندات من لوحة الإدارة.'}, {'title':'后台审核','description':'人力资源团队在后台审核申请人和文件。'}),
            'Interview Invite': ({'title':'دعوة المقابلة','description':'يتلقى المرشحون المختارون تاريخ ومكان وتعليمات المقابلة عبر البريد الإلكتروني.'}, {'title':'面试邀请','description':'入围申请人将通过电子邮件收到面试日期、地点和说明。'}),
            'Selection': ({'title':'الاختيار','description':'يتم اختيار المرشحين النهائيين حسب متطلبات الوظيفة واحتياجات المشروع.'}, {'title':'录用选择','description':'最终候选人根据职位要求和项目需要选择。'}),
        }
        for step in CareerProcessStep.objects.all():
            values = process_map.get(step.title)
            if values:
                ar_map, zh_map = values; many(step,'ar',ar_map); many(step,'zh-hans',zh_map)
        for dept in CareerDepartment.objects.all():
            dept_ar={'Engineering':'الهندسة','HSE & Quality':'السلامة والجودة','Administration':'الإدارة'}.get(dept.name, dept.name)
            dept_zh={'Engineering':'工程','HSE & Quality':'安全与质量','Administration':'行政'}.get(dept.name, dept.name)
            many(dept,'ar',{'name':dept_ar,'description':'قسم للفرص الوظيفية في SESCCO.'}); many(dept,'zh-hans',{'name':dept_zh,'description':'SESCCO 职业机会部门。'})
        job_ar_map = {
            "Electrical Site Engineer": {
                "title": "مهندس كهرباء موقع",
                "summary": "تنسيق أعمال الكهرباء في الموقع ومراجعة الرسومات ودعم التنفيذ اليومي للمشاريع الصناعية.",
                "job_description": "يدعم مهندس الكهرباء الميداني التنفيذ اليومي وتنسيق الرسومات ومتابعة المواد وإعداد تقارير الموقع لفرق مشاريع SESCCO.\n\nتتطلب الوظيفة تنسيقاً عملياً في الموقع وانضباطاً ووعياً بالسلامة وتواصلاً واضحاً مع المشرفين وفريق الجودة وممثلي العميل.",
                "responsibilities": "تنسيق أنشطة الكهرباء اليومية في الموقع.\nمراجعة الرسومات ومتطلبات المواد وواجهات العمل.\nالتنسيق مع المشرفين وفريق الجودة وممثلي العميل.\nإعداد تحديثات التقدم ودعم التنفيذ الآمن.",
                "requirements": "درجة أو دبلوم في الهندسة الكهربائية.\nخبرة لا تقل عن 3 سنوات في المواقع.\nمعرفة قوية بالرسومات والمواد وتنسيق الموقع.\nمهارات جيدة في التواصل والتوثيق.",
                "qualifications": "درجة أو دبلوم في الهندسة الكهربائية.\nيفضل وجود خبرة في مواقع المشاريع السعودية.\nالقدرة على قراءة الرسومات والمستندات الفنية.",
                "skills": "تنسيق الموقع.\nمراجعة الرسومات.\nإعداد التقارير اليومية.\nالتواصل المتعلق بالسلامة.",
                "benefits": "حزمة تنافسية حسب الخبرة.\nبيئة مشاريع احترافية.\nفرصة للعمل في مشاريع صناعية وبنية تحتية.",
                "location": "الدمام، المملكة العربية السعودية",
                "experience_level": "3 سنوات فأكثر",
            },
            "HSE Officer": {
                "title": "مسؤول السلامة والصحة المهنية",
                "summary": "دعم تطبيق السلامة في الموقع والتفتيش واجتماعات السلامة والتوثيق.",
                "job_description": "يدعم مسؤول السلامة والصحة المهنية ممارسات العمل الآمنة في مواقع المشاريع من خلال التفتيش واجتماعات السلامة والتقارير والمتابعة مع فريق الموقع.\n\nتناسب هذه الوظيفة المرشحين المنظمين والعمليين والملتزمين بالحفاظ على معايير السلامة في مواقع الإنشاء أو المشاريع الصناعية.",
                "responsibilities": "تنفيذ جولات تفتيش وملاحظات السلامة في الموقع.\nدعم اجتماعات السلامة والتوعية اليومية.\nحفظ سجلات السلامة ودعم تقارير الحوادث.\nالتنسيق مع فرق المشروع لإغلاق إجراءات السلامة.",
                "requirements": "دبلوم أو مؤهل مناسب في السلامة.\nيفضل الحصول على شهادة NEBOSH أو OSHA.\nخبرة في مواقع الإنشاء أو المشاريع الصناعية.\nمهارات جيدة في التقارير والتواصل.",
                "qualifications": "يفضل وجود شهادة سلامة مناسبة.\nمعرفة بتوثيق السلامة في المواقع.\nالقدرة على التواصل مع العمال والمشرفين.",
                "skills": "تقارير التفتيش.\nدعم اجتماعات السلامة.\nتوثيق الحوادث.\nمتابعة الإجراءات التصحيحية.",
                "benefits": "ثقافة عمل تركز على السلامة.\nخبرة في مشاريع داخل المملكة.\nفرصة نمو داخل وظيفة السلامة والصحة المهنية.",
                "location": "المنطقة الشرقية، المملكة العربية السعودية",
                "experience_level": "سنتان فأكثر",
            },
            "Document Controller": {
                "title": "منسق مستندات",
                "summary": "إدارة مستندات المشاريع والمراسلات والسجلات والوثائق المضبوطة لفريق الهندسة.",
                "job_description": "يحافظ منسق المستندات على تنظيم مستندات المشاريع والسجلات والإرسالات وتتبع المراجعات لفرق المكتب والمشاريع.\n\nتتطلب الوظيفة الدقة والانضباط في حفظ الملفات ومعرفة Excel والمتابعة المهنية مع الأقسام الداخلية.",
                "responsibilities": "حفظ سجلات المستندات الواردة والصادرة.\nالتحكم في المراجعات والإرسالات والاعتمادات.\nالتنسيق مع فرق المشاريع والإدارة.\nتنظيم السجلات الرقمية والورقية.",
                "requirements": "خبرة في ضبط المستندات أو إدارة المشاريع.\nمهارات قوية في Excel وإدارة الملفات.\nاهتمام بالتفاصيل وتواصل مهني.\nيفضل التواصل بالعربية والإنجليزية.",
                "qualifications": "يفضل دبلوم أو خلفية في الإدارة المكتبية.\nخبرة ضبط المستندات ميزة إضافية.\nمهارات جيدة في الحاسب وحفظ الملفات.",
                "skills": "سجلات Excel.\nتسمية الملفات والأرشفة.\nتنسيق البريد الإلكتروني.\nمتابعة الإرسالات.",
                "benefits": "وظيفة مكتبية.\nآلية مستندات منظمة.\nنمو طويل الأمد في إدارة المشاريع.",
                "location": "مكتب الدمام",
                "experience_level": "سنة فأكثر",
            },
        }
        job_zh_map = {
            "Electrical Site Engineer": {
                "title": "现场电气工程师",
                "summary": "负责工业项目现场电气工作协调、图纸审核和日常执行支持。",
                "job_description": "现场电气工程师为 SESCCO 项目团队提供日常执行、图纸协调、材料跟进和现场报告支持。\n\n该岗位需要实际现场协调能力、纪律意识、安全意识，并能与主管、QA/QC 和客户代表清晰沟通。",
                "responsibilities": "协调每日现场电气活动。\n审核图纸、材料需求和工作面。\n与主管、QA/QC 和客户代表协调。\n准备进度更新并支持安全施工。",
                "requirements": "电气工程学位或文凭。\n至少 3 年现场经验。\n熟悉图纸、材料和现场协调。\n具备良好的沟通和文件记录能力。",
                "qualifications": "电气工程学位或文凭。\n有沙特项目现场经验者优先。\n能够阅读图纸和技术文件。",
                "skills": "现场协调。\n图纸审核。\n日报编制。\n安全沟通。",
                "benefits": "根据经验提供有竞争力的待遇。\n专业项目环境。\n有机会参与工业和基础设施项目。",
                "location": "沙特阿拉伯达曼",
                "experience_level": "3 年以上",
            },
            "HSE Officer": {
                "title": "HSE 安全员",
                "summary": "支持现场安全实施、检查、班前安全会和安全文件记录。",
                "job_description": "HSE 安全员通过检查、班前安全会、报告和现场团队跟进，支持项目现场的安全工作实践。\n\n该岗位适合组织能力强、务实并致力于在施工或工业现场保持安全标准的候选人。",
                "responsibilities": "开展现场安全检查和观察。\n支持班前安全会和安全简报。\n维护安全记录并支持事故报告。\n与项目团队协调关闭安全整改事项。",
                "requirements": "安全相关文凭或资格。\n持有 NEBOSH / OSHA 证书者优先。\n具有施工或工业项目现场经验。\n具备良好的报告和沟通能力。",
                "qualifications": "优先考虑相关安全证书。\n了解现场安全文件。\n能够与工人和主管沟通。",
                "skills": "检查报告。\n班前安全会支持。\n事故文件记录。\n纠正措施跟进。",
                "benefits": "重视安全的工作文化。\n接触沙特各地项目。\n在 HSE 职能中获得成长机会。",
                "location": "沙特阿拉伯东部省",
                "experience_level": "2 年以上",
            },
            "Document Controller": {
                "title": "文件控制员",
                "summary": "为工程团队管理项目文件、提交资料、登记表和受控记录。",
                "job_description": "文件控制员负责为办公室和项目团队维护有序的项目文件、登记表、提交资料和版本跟踪。\n\n该岗位需要准确性、文件纪律、Excel 知识以及与内部部门的专业跟进。",
                "responsibilities": "维护收发文件登记表。\n控制版本、提交和审批。\n与项目和行政团队协调。\n保持电子和纸质记录有序。",
                "requirements": "具有文件控制或项目行政经验。\n熟练掌握 Excel 和文件管理。\n注重细节并具备专业沟通能力。\n优先考虑阿拉伯语和英语沟通能力。",
                "qualifications": "优先考虑文凭或办公室行政背景。\n有文件控制经验者更佳。\n具备良好的电脑和归档技能。",
                "skills": "Excel 登记表。\n文件命名与归档。\n邮件协调。\n提交跟踪。",
                "benefits": "办公室岗位。\n结构化文件流程。\n在项目行政方向长期成长。",
                "location": "达曼办公室",
                "experience_level": "1 年以上",
            },
        }
        for job in JobOpening.objects.all():
            ar = job_ar_map.get(job.title, {})
            zh = job_zh_map.get(job.title, {})
            ar_base = {
                'title': ar.get('title', f"فرصة وظيفية: {job.title}"),
                'summary': ar.get('summary', 'فرصة وظيفية لدى SESCCO للمرشحين المؤهلين.'),
                'job_description': ar.get('job_description', 'هذه وظيفة منشورة من خلال نظام الوظائف القابل للإدارة في SESCCO ويمكن تحديث تفاصيلها من لوحة التحكم.'),
                'responsibilities': ar.get('responsibilities', 'تنفيذ مسؤوليات الوظيفة حسب متطلبات المشروع.\nالتنسيق مع فريق العمل والإدارة.\nالالتزام بمعايير السلامة والجودة.'),
                'requirements': ar.get('requirements', 'خبرة مناسبة حسب متطلبات الوظيفة.\nمهارات تواصل وتوثيق جيدة.\nالالتزام بمتطلبات الموقع والمشروع.'),
                'qualifications': ar.get('qualifications', 'مؤهل مناسب لطبيعة الوظيفة.\nخبرة عملية ذات صلة ميزة إضافية.'),
                'skills': ar.get('skills', 'التنسيق.\nالتواصل.\nإعداد التقارير.\nالعمل الجماعي.'),
                'benefits': ar.get('benefits', 'بيئة عمل مهنية.\nفرص نمو داخل المشاريع.\nمراجعة عادلة للطلبات.'),
                'location': ar.get('location', 'المملكة العربية السعودية'),
                'experience_level': ar.get('experience_level', 'خبرة مناسبة'),
                'salary_range': 'غير معلن' if not job.salary_range else job.salary_range,
                'salary_note': 'حسب الخبرة ومتطلبات الوظيفة',
                'apply_button_text': 'قدم الآن',
                'seo_title': f"{ar.get('title', job.title)} | وظائف SESCCO",
                'seo_description': ar.get('summary', 'فرصة وظيفية لدى SESCCO للمرشحين المؤهلين.'),
            }
            zh_base = {
                'title': zh.get('title', f"职位机会：{job.title}"),
                'summary': zh.get('summary', 'SESCCO 面向合格候选人的职位机会。'),
                'job_description': zh.get('job_description', '这是通过 SESCCO 招聘 CMS 发布的职位，管理员可在后台更新职位详情。'),
                'responsibilities': zh.get('responsibilities', '根据项目要求履行岗位职责。\n与团队和管理层协调。\n遵守安全和质量标准。'),
                'requirements': zh.get('requirements', '符合岗位要求的相关经验。\n具备良好的沟通和文件记录能力。\n遵守现场和项目要求。'),
                'qualifications': zh.get('qualifications', '与岗位性质相符的资格。\n相关实际经验者优先。'),
                'skills': zh.get('skills', '协调。\n沟通。\n报告。\n团队合作。'),
                'benefits': zh.get('benefits', '专业工作环境。\n项目内成长机会。\n公平的申请审核流程。'),
                'location': zh.get('location', '沙特阿拉伯'),
                'experience_level': zh.get('experience_level', '相关经验'),
                'salary_range': '未公开' if not job.salary_range else job.salary_range,
                'salary_note': '根据经验和岗位要求确定',
                'apply_button_text': '立即申请',
                'seo_title': f"{zh.get('title', job.title)} | SESCCO 招聘",
                'seo_description': zh.get('summary', 'SESCCO 面向合格候选人的职位机会。'),
            }
            many(job,'ar', ar_base)
            many(job,'zh-hans', zh_base)

        highlight_map = {
            "Integrated Engineering": (
                {"title": "هندسة متكاملة", "value": "تخصصات متعددة", "description": "خدمات كهربائية ومدنية ومعمارية وتشطيبات ودعم ضمن فريق موثوق.", "link_text": "اعرف المزيد"},
                {"title": "综合工程", "value": "多专业能力", "description": "电气、土建、建筑装修和支持服务，由可靠团队统一执行。", "link_text": "了解更多"},
            ),
            "Project Execution Support": (
                {"title": "دعم جاهز للمشاريع", "value": "فرق مؤهلة", "description": "عمالة ماهرة ودعم معدات وتنفيذ عملي لبيئات المشاريع المتطلبة.", "link_text": "اعرف المزيد"},
                {"title": "项目支持能力", "value": "合格团队", "description": "为复杂项目环境提供熟练人员、设备支持和实用执行。", "link_text": "了解更多"},
            ),
            "Safety & Quality Focus": (
                {"title": "السلامة والجودة", "value": "تسليم موثوق", "description": "تنفيذ يستند إلى السلامة والجودة والكفاءة وبناء ثقة طويلة الأمد.", "link_text": "اعرف المزيد"},
                {"title": "安全与质量", "value": "可靠交付", "description": "以安全、质量、效率和长期客户信任为指导的执行。", "link_text": "了解更多"},
            ),
        }
        home_highlights = HomeHighlight.objects.all()
        for item in home_highlights:
            if item.title in highlight_map:
                ar_map, zh_map = highlight_map[item.title]
                set_many(item, "ar", ar_map)
                set_many(item, "zh-hans", zh_map)



        # Upgrade 123 localization coverage for newly seeded completion sections.
        section_map = {
            "Integrated Capabilities": (
                {"title": "قدرات متكاملة", "subtitle": "شركة واحدة للاحتياجات الكهربائية والمدنية والتشطيبات والدعم التعاقدي.", "content": "<p>تجمع SESCCO بين القدرات الهندسية العملية والفرق الجاهزة للموقع والمصداقية المسجلة لدى الجهات الرئيسية.</p>", "button_text": "استعرض الخدمات"},
                {"title": "综合能力", "subtitle": "一家公司满足电气、土建、装修、机械和合同支持需求。", "content": "<p>SESCCO 将实用工程能力、现场就绪团队和供应商注册信誉结合起来，服务工业、公用事业和商业项目。</p>", "button_text": "查看服务"},
            ),
            "Experience Across Saudi Arabia": (
                {"title": "خبرة في أنحاء المملكة", "subtitle": "مراجع مشاريع مبنية على تنفيذ موثوق.", "content": "<p>تعكس محفظة SESCCO خبرة ميدانية حقيقية في أعمال المحطات والكابلات والأعمال المدنية والأنابيب والتشطيبات.</p>", "button_text": "عرض المشاريع"},
                {"title": "沙特各地项目经验", "subtitle": "以可靠执行建立的项目参考。", "content": "<p>从变电站接口工程和电缆端接到土建、管线支持和装修交付，SESCCO 的项目组合体现真实现场经验。</p>", "button_text": "查看项目"},
            ),
            "What Makes SESCCO Reliable": (
                {"title": "ما الذي يجعل SESCCO موثوقة", "subtitle": "تنفيذ منظم وفرق مؤهلة وتواصل واضح.", "content": "<p>يعتمد عملنا على السلامة والجودة واحترام الناس وبناء علاقات طويلة الأمد مع العملاء.</p>", "button_text": "تواصل مع SESCCO"},
                {"title": "SESCCO 为何可靠", "subtitle": "结构化交付、合格团队和清晰沟通。", "content": "<p>我们的工作以安全、质量、尊重人员和长期客户关系为指导。</p>", "button_text": "联系 SESCCO"},
            ),
            "Need more information?": (
                {"title": "هل تحتاج إلى معلومات إضافية؟", "subtitle": "يمكن لفريقنا مشاركة المستند أو تفاصيل الخدمة المناسبة لمتطلباتك.", "content": "<p>تواصل مع SESCCO بخصوص مشروعك أو طلب المستندات أو التأهيل.</p>", "button_text": "اتصل بنا"},
                {"title": "需要更多信息？", "subtitle": "我们的团队可根据您的需求提供合适文件或服务详情。", "content": "<p>请联系 SESCCO，说明您的项目、文件或资格资料需求。</p>", "button_text": "联系我们"},
            ),
        }
        for section in PageSection.objects.all():
            values = section_map.get(section.title)
            if values:
                ar_map, zh_map = values
                set_many(section, "ar", ar_map)
                set_many(section, "zh-hans", zh_map)

        page_map = {
            "quality-safety": (
                {"title": "الجودة والسلامة", "hero_title": "التزام الجودة والسلامة", "hero_subtitle": "تنفيذ يستند إلى السلامة والجودة وضبط المشاريع.", "body": "<p>تعطي SESCCO الأولوية لممارسات العمل الآمنة والتنفيذ عالي الجودة واحترام الناس والبيئة.</p>", "seo_title": "الجودة والسلامة | SESCCO", "seo_description": "التزام SESCCO بالجودة والسلامة."},
                {"title": "质量与安全", "hero_title": "质量与安全承诺", "hero_subtitle": "以安全、质量和负责任项目控制为指导的执行。", "body": "<p>SESCCO 重视安全工作实践、质量执行以及对人员和环境的尊重。</p>", "seo_title": "质量与安全 | SESCCO", "seo_description": "SESCCO 的质量与安全承诺。"},
            ),
            "vendor-registration": (
                {"title": "تسجيل الموردين", "hero_title": "معلومات تسجيل الموردين", "hero_subtitle": "بيانات رئيسية للمراجعة والتأهيل.", "body": "<p>تدرج SESCCO رمز مورد أرامكو السعودية <strong>10114560</strong> ورمز مورد الشركة السعودية للكهرباء <strong>02013075</strong>.</p>", "seo_title": "تسجيل الموردين | SESCCO", "seo_description": "معلومات تسجيل الموردين لدى SESCCO."},
                {"title": "供应商注册", "hero_title": "供应商注册信息", "hero_subtitle": "用于项目和采购审核的关键资质信息。", "body": "<p>SESCCO 公司资料列出沙特阿美供应商代码 <strong>10114560</strong> 和沙特电力公司供应商代码 <strong>02013075</strong>。</p>", "seo_title": "供应商注册 | SESCCO", "seo_description": "SESCCO 供应商注册信息。"},
            ),
            "capabilities": (
                {"title": "القدرات", "hero_title": "قدرات الهندسة والمقاولات", "hero_subtitle": "نظرة واضحة على قدرات SESCCO الخدمية.", "body": "<p>تشمل القدرات الأساسية الهندسة الكهربائية، الأعمال المدنية والمعمارية والتشطيبات، الدعم التعاقدي، أنظمة التكييف، أنظمة إنذار الحريق، السباكة، أنظمة الإطفاء، وإنارة وطاقة المباني.</p>", "seo_title": "القدرات | SESCCO", "seo_description": "قدرات SESCCO الهندسية والمقاولات."},
                {"title": "能力", "hero_title": "工程与承包能力", "hero_subtitle": "清晰展示 SESCCO 的服务能力。", "body": "<p>核心能力包括电气工程、土建与建筑装修、合同支持、暖通、火灾探测报警、给排水、消防系统以及建筑照明和电力系统。</p>", "seo_title": "能力 | SESCCO", "seo_description": "SESCCO 的工程与承包能力。"},
            ),
        }
        for page_obj in Page.objects.filter(slug__in=page_map.keys()):
            ar_map, zh_map = page_map[page_obj.slug]
            set_many(page_obj, "ar", ar_map)
            set_many(page_obj, "zh-hans", zh_map)

        faq_map = {
            "What is SESCCO’s core business?": ("ما هو نشاط SESCCO الأساسي؟", "تقدم SESCCO خدمات الهندسة الكهربائية والأعمال المدنية والمعمارية والتشطيبات والأعمال الكهروميكانيكية والميكانيكية ومكافحة الحريق والدعم التعاقدي.", "SESCCO 的核心业务是什么？", "SESCCO 提供电气工程、土建与建筑装修、机电、机械与消防支持以及合同支持服务。"),
            "Is SESCCO registered with major Saudi clients?": ("هل SESCCO مسجلة لدى جهات سعودية رئيسية؟", "نعم، يذكر ملف الشركة رمز مورد أرامكو السعودية 10114560 ورمز مورد الشركة السعودية للكهرباء 02013075.", "SESCCO 是否在沙特主要客户处注册？", "是的，公司资料列出沙特阿美供应商代码 10114560 和沙特电力公司供应商代码 02013075。"),
            "Where is SESCCO based?": ("أين يقع مقر SESCCO؟", "يقع مقر SESCCO في الدمام، المنطقة الشرقية، المملكة العربية السعودية، وتدعم المشاريع في أنحاء المملكة حسب المتطلبات.", "SESCCO 位于哪里？", "SESCCO 位于沙特阿拉伯东部省达曼，并可根据项目需求支持沙特各地项目。"),
            "What makes SESCCO a dependable partner?": ("ما الذي يجعل SESCCO شريكاً موثوقاً؟", "تركز الشركة على السلامة والجودة والكوادر المؤهلة والخدمة الموثوقة والعلاقات طويلة الأمد المبنية على الثقة والاحترام.", "SESCCO 为什么是可靠伙伴？", "公司重视安全、质量、合格人员、可靠服务以及建立在信任和尊重基础上的长期客户关系。"),
            "Can this information be updated from admin?": ("هل يمكن تحديث هذه المعلومات من لوحة الإدارة؟", "نعم. يمكن تعديل هذه الصفحة وأقسام CMS الخاصة بها من لوحة إدارة Django.", "这些信息可以从后台更新吗？", "可以。此页面及其自定义 CMS 区块可从 Django 后台编辑。"),
        }
        for faq in FAQ.objects.all():
            values = faq_map.get(faq.question)
            if values:
                ar_q, ar_a, zh_q, zh_a = values
                set_many(faq, "ar", {"question": ar_q, "answer": f"<p>{ar_a}</p>"})
                set_many(faq, "zh-hans", {"question": zh_q, "answer": f"<p>{zh_a}</p>"})

        project_scope_map = {
            "Scope review": ({"title": "مراجعة النطاق", "description": "مراجعة متطلبات المشروع والموقع والرسومات وقيود التنفيذ قبل التعبئة."}, {"title": "范围审核", "description": "动员前审核项目要求、位置、图纸和执行限制。"}),
            "Site execution": ({"title": "تنفيذ الموقع", "description": "تنسيق القوى العاملة والمواد وفحوصات الجودة أثناء مرحلة العمل."}, {"title": "现场执行", "description": "在施工阶段协调人力、材料和质量检查。"}),
            "Handover support": ({"title": "دعم التسليم", "description": "دعم سجلات الإكمال ومعلومات الإغلاق والمتابعة عند الحاجة."}, {"title": "移交支持", "description": "根据需要支持完工记录、收尾资料和后续协调。"}),
        }
        for item in ProjectScopeItem.objects.all():
            values = project_scope_map.get(item.title)
            if values:
                ar_map, zh_map = values
                set_many(item, "ar", ar_map)
                set_many(item, "zh-hans", zh_map)


        # Upgrade 124: localized titles for additional company-profile projects
        # seeded from the English profile. Scope item translations are concise
        # but meaningful so Arabic/Chinese project detail pages are not left with
        # English-only production data.
        upgrade_124_project_map = {
            "Dismantling and Transportation of TFC at Haradh": (
                "تفكيك ونقل معدات TFC في هرض",
                "هرض TFC 拆除与运输项目",
            ),
            "Preparation and Painting of 230kV OHTL Foundation": (
                "تحضير ودهان أساسات أبراج خط هوائي 230 ك.ف",
                "230kV 架空输电线路基础处理与涂装",
            ),
            "The Avenues Khobar Plaster Works": (
                "أعمال اللياسة في ذا أفنيوز الخبر",
                "The Avenues Khobar 抹灰工程",
            ),
            "The Avenues Khobar Screed Works": (
                "أعمال السكريد في ذا أفنيوز الخبر",
                "The Avenues Khobar 找平层工程",
            ),
            "Mansura Massrah Gold Project Civil Works": (
                "الأعمال المدنية لمشروع منصورة مسرة للذهب",
                "Mansura Massrah 金矿项目土建工程",
            ),
            "Novartis Office MEP and Architectural Fitout": (
                "أعمال MEP والتشطيبات المعمارية لمكتب نوفارتس",
                "Novartis 办公室机电与建筑装修工程",
            ),
        }
        for project in Project.objects.filter(title__in=upgrade_124_project_map.keys()):
            ar_title, zh_title = upgrade_124_project_map[project.title]
            set_many(project, "ar", {
                "title": ar_title,
                "short_description": "مشروع حقيقي من ملف الشركة يعكس خبرة SESCCO في التنفيذ الميداني.",
                "summary": "<p>يعكس هذا المشروع إحدى خبرات SESCCO الموثقة في ملف الشركة، مع تركيز على التنفيذ الميداني المنظم ومتطلبات العميل.</p>",
                "challenge": "<p>تطلب العمل تنسيقاً ميدانياً دقيقاً وتنفيذاً آمناً وفق متطلبات العميل.</p>",
                "scope": "<p>شمل نطاق العمل أنشطة تنفيذ ومتابعة وتنسيق فني مناسبة لطبيعة المشروع.</p>",
                "solution": "<p>قدمت SESCCO دعماً عملياً من خلال فرق مؤهلة وإشراف منظم.</p>",
                "outcomes": "<p>يعزز المشروع خبرة SESCCO الموثقة في ملف الشركة.</p>",
                "seo_title": f"{ar_title} | خبرات SESCCO",
                "seo_description": "مشروع ضمن خبرات SESCCO المستندة إلى ملف الشركة.",
            })
            set_many(project, "zh-hans", {
                "title": zh_title,
                "short_description": "来自公司简介的真实项目，体现 SESCCO 的现场执行经验。",
                "summary": "<p>该项目来自 SESCCO 公司简介，体现了公司在现场执行、协调和客户要求管理方面的经验。</p>",
                "challenge": "<p>工作需要严格的现场协调，并按照客户要求安全执行。</p>",
                "scope": "<p>工作范围包括适合项目性质的执行、跟进和技术协调活动。</p>",
                "solution": "<p>SESCCO 通过合格团队和有序监督提供实际支持。</p>",
                "outcomes": "<p>该项目加强了 SESCCO 公司简介中的项目经验展示。</p>",
                "seo_title": f"{zh_title} | SESCCO 项目经验",
                "seo_description": "基于 SESCCO 公司简介的项目经验。",
            })

        upgrade_124_scope_map = {
            "Dismantling works": ({"title": "أعمال التفكيك", "description": "تفكيك المعدات الكهربائية والعناصر المرتبطة بالموقع."}, {"title": "拆除工作", "description": "拆除电气设备及相关现场构件。"}),
            "Transportation support": ({"title": "دعم النقل", "description": "تنسيق نقل المعدات والمواد التي تمت إزالتها."}, {"title": "运输支持", "description": "协调已拆除设备和项目材料的运输。"}),
            "Demolition and disposal": ({"title": "الهدم والتخلص", "description": "هدم والتخلص من عناصر TFC حسب متطلبات المشروع."}, {"title": "拆除与处理", "description": "按项目要求拆除并处理 TFC 构件。"}),
            "Surface preparation": ({"title": "تحضير السطح", "description": "تحضير أسطح أساسات أبراج 230 ك.ف قبل الدهان."}, {"title": "表面处理", "description": "在涂装前处理 230kV 塔基表面。"}),
            "Paint supply": ({"title": "توريد الدهان", "description": "توريد مواد الدهان المعتمدة حسب متطلبات المشروع."}, {"title": "涂料供应", "description": "根据项目要求供应合格涂料。"}),
            "Foundation painting": ({"title": "دهان الأساسات", "description": "تنفيذ دهان الأساسات وفق معيار SEC."}, {"title": "基础涂装", "description": "按 SEC 标准完成基础涂装。"}),
            "Plaster works": ({"title": "أعمال اللياسة", "description": "لياسة غرف الصلاة والحمامات والممرات والمناطق المرتبطة."}, {"title": "抹灰工程", "description": "用于祈祷室、卫生间、走廊和相关区域的抹灰。"}),
            "Mesh installation": ({"title": "تركيب الشبك", "description": "تركيب الشبك لدعم الأسطح المعمارية المحضرة."}, {"title": "网格安装", "description": "为准备好的建筑表面安装网格。"}),
            "Angle installation": ({"title": "تركيب الزوايا", "description": "تركيب الزوايا وتنسيق التشطيبات للأسطح الداخلية."}, {"title": "角条安装", "description": "内表面角条安装与装修协调。"}),
            "Screed works": ({"title": "أعمال السكريد", "description": "تنفيذ طبقات السكريد للمناطق الداخلية المحددة."}, {"title": "找平层工程", "description": "为指定室内区域施工找平层。"}),
            "Area coordination": ({"title": "تنسيق المناطق", "description": "تنسيق واجهات العمل عبر مناطق داخلية متعددة."}, {"title": "区域协调", "description": "协调多个室内区域的工作面。"}),
            "Finishing support": ({"title": "دعم التشطيبات", "description": "دعم الأسطح المستوية والمتينة للأنشطة اللاحقة."}, {"title": "装修支持", "description": "为后续装修活动提供平整耐用表面。"}),
            "Substation building": ({"title": "مبنى المحطة", "description": "دعم الأعمال المدنية لمبنى المحطة والبنية المرتبطة."}, {"title": "变电站建筑", "description": "支持变电站建筑和相关基础设施土建工作。"}),
            "Industrial structures": ({"title": "هياكل صناعية", "description": "حزم أعمال للأنفاق وحوامل الأنابيب والسيور والمستودعات."}, {"title": "工业结构", "description": "管廊、隧道、输送带、发动机大厅和仓库工作包。"}),
            "Tank and utility works": ({"title": "الخزانات والمرافق", "description": "دعم إنشاء خزانات ومرافق صناعية مرتبطة."}, {"title": "储罐与公用工程", "description": "支持水罐、燃油设施及地下/地上储罐施工。"}),
            "MEP structure": ({"title": "هيكل MEP", "description": "أعمال هيكلية للأنظمة الميكانيكية والكهربائية والسباكة داخل المكتب."}, {"title": "机电结构", "description": "办公室机电给排水系统结构工作。"}),
            "Architectural covering": ({"title": "التغطيات المعمارية", "description": "تغطيات وتشطيبات معمارية لمساحة تقارب 1,300 متر مربع."}, {"title": "建筑覆盖", "description": "约 1,300 平方米的建筑覆盖与室内装修。"}),
            "Office delivery": ({"title": "تسليم المكتب", "description": "تنفيذ منسق لبيئة مكتب مؤسسية."}, {"title": "办公室交付", "description": "面向企业办公室环境的协调交付。"}),
        }
        for item in ProjectScopeItem.objects.all():
            values = upgrade_124_scope_map.get(item.title)
            if values:
                ar_map, zh_map = values
                set_many(item, "ar", ar_map)
                set_many(item, "zh-hans", zh_map)


        # Upgrade 125 localization for expanded document center.
        doc_category_map = {
            "Service Capability Sheets": ({"name": "ملفات قدرات الخدمات"}, {"name": "服务能力文件"}),
            "Vendor & Compliance Documents": ({"name": "مستندات الموردين والامتثال"}, {"name": "供应商与合规文件"}),
            "Company Documents": ({"name": "مستندات الشركة"}, {"name": "公司文件"}),
        }
        for category in DocumentCategory.objects.all():
            values = doc_category_map.get(category.name)
            if values:
                ar_map, zh_map = values
                set_many(category, "ar", ar_map)
                set_many(category, "zh-hans", zh_map)

        for doc in DownloadDocument.objects.all():
            if "Capability Sheet" in doc.title:
                set_many(doc, "ar", {
                    "title": doc.title.replace("Capability Sheet", "ملف القدرات"),
                    "description": "مرجع قابل للتنزيل يوضح قدرات SESCCO وخدماتها وخبراتها العملية.",
                })
                set_many(doc, "zh-hans", {
                    "title": doc.title.replace("Capability Sheet", "能力文件"),
                    "description": "可下载参考文件，介绍 SESCCO 的能力、服务和项目经验。",
                })
            elif "Vendor Code" in doc.title or "Vendor" in doc.title:
                set_many(doc, "ar", {"description": "مرجع بيانات الموردين والاعتماد الخاصة بـ SESCCO."})
                set_many(doc, "zh-hans", {"description": "SESCCO 供应商与注册信息参考。"})
            elif "Quality" in doc.title or "Safety" in doc.title:
                set_many(doc, "ar", {"description": "مرجع التزام SESCCO بالجودة والسلامة والمسؤولية البيئية."})
                set_many(doc, "zh-hans", {"description": "SESCCO 关于质量、安全与环境责任的承诺参考。"})

        downloads_settings = DownloadsPageSettings.objects.first()
        if downloads_settings:
            set_many(downloads_settings, "ar", {
                "eyebrow": "التحميلات",
                "hero_title": "ملف الشركة والمستندات الرئيسية",
                "hero_subtitle": "تحميل ملف الشركة وملفات القدرات ومراجع الموردين والامتثال.",
                "intro_title": "مركز المستندات",
                "intro_text": "<p>استعرض مستندات SESCCO العامة أو اطلب مستنداً محدداً من الفريق.</p>",
            })
            set_many(downloads_settings, "zh-hans", {
                "eyebrow": "下载",
                "hero_title": "公司简介与关键文件",
                "hero_subtitle": "下载公司简介、能力文件、供应商参考和合规文件。",
                "intro_title": "文件中心",
                "intro_text": "<p>浏览 SESCCO 公开文件，或向团队申请特定文件。</p>",
            })


        # Upgrade 165 — ensure CTA CMS records stay localized after reseeding.
        for service_cta in ServiceCTA.objects.all():
            set_many(service_cta, "ar", {
                "title": "هل تحتاج إلى دعم لهذا العمل؟",
                "subtitle": "تواصل مع SESCCO لمناقشة متطلبات مشروعك.",
                "button_text": "اطلب عرضاً",
            })
            set_many(service_cta, "zh-hans", {
                "title": "需要此项工作的支持？",
                "subtitle": "请联系 SESCCO 讨论您的项目需求。",
                "button_text": "获取报价",
            })

        for project_cta in ProjectCTA.objects.all():
            set_many(project_cta, "ar", {
                "title": "هل لديك مشروع مشابه؟",
                "subtitle": "تواصل مع SESCCO لمناقشة متطلباتك الهندسية أو التعاقدية.",
                "button_text": "ابدأ مشروعاً",
            })
            set_many(project_cta, "zh-hans", {
                "title": "需要类似项目支持？",
                "subtitle": "请联系 SESCCO 讨论您的工程或承包需求。",
                "button_text": "启动项目",
            })

        document_cta = DocumentPageCTA.objects.first()
        if document_cta:
            set_many(document_cta, "ar", {
                "title": "هل تحتاج إلى مستند محدد؟",
                "subtitle": "أخبرنا بالمستند الذي تحتاجه وسيرد فريق SESCCO بالمعلومات المناسبة.",
                "button_text": "طلب مستند",
            })
            set_many(document_cta, "zh-hans", {
                "title": "需要特定文件？",
                "subtitle": "请告诉我们您需要的文件，SESCCO 团队会提供相应信息。",
                "button_text": "申请文件",
            })

        self.stdout.write(self.style.SUCCESS('SESCCO localization seeded successfully.'))
