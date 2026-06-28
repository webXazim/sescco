import json
from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.core.models import CompanyProfile, SiteSettings, ThemeSettings, NavigationMenu, FooterColumn, FooterLink, CTASettings, SocialLink, TrustMetric, CTASection, OfficeLocation, BusinessHour, ContactMethod, LocalizedContent
from apps.pages.models import Page, PageSection, StatItem, TimelineItem, FAQ, HomeHero, HomeAboutBlock, HomeSectionSettings, WhyChooseItem, HomeHighlight, ValueItem, MissionVisionItem, LeadershipMessage, AboutPageSettings, GenericPageSettings, PageSectionOrder
from apps.services.models import ServiceCategory, Service, ServiceDeliverable, ServiceProcessStep, ServiceFAQ, ServiceListPageSettings, ServiceListProcessStep, ServiceListFAQ, ServiceKeyPoint, ServiceFeature, ServiceCTA, ServiceDetailPageSettings
from apps.projects.models import ProjectCategory, Project, ProjectMetric, ProjectImage, ProjectListPageSettings, ProjectListStat, ProjectScopeItem, ProjectCTA, ProjectDetailPageSettings
from apps.clients.models import Client, Partner, Certificate, Accreditation, Standard, Testimonial, TrustPageSettings, TrustMetric as ClientTrustMetric, ClientCategory, CertificateCategory, ComplianceBlock
from apps.documents.models import DocumentCategory, DownloadDocument, DownloadsPageSettings, DocumentPageCTA
from apps.careers.models import (
    CareerBenefit,
    CareerDepartment,
    CareerPageSettings,
    CareerProcessStep,
    CareerStat,
    DEFAULT_EMAIL_VERIFICATION_BODY,
    DEFAULT_EMAIL_VERIFICATION_SUBJECT,
    DEFAULT_INTERVIEW_EMAIL_BODY,
    DEFAULT_INTERVIEW_EMAIL_SUBJECT,
    DEFAULT_REJECTION_EMAIL_BODY,
    DEFAULT_REJECTION_EMAIL_SUBJECT,
    JobOpening,
)
from apps.inquiries.models import InquirySubject, ContactPageSettings
from apps.seo.models import RobotsSettings, SchemaMarkup



def set_loc(obj, lang, field, text):
    if not obj or not getattr(obj, "id", None):
        return
    LocalizedContent.objects.update_or_create(
        content_type=obj.__class__.__name__.lower(),
        object_id=obj.id,
        language_code=lang,
        field_name=field,
        defaults={"text": text},
    )

def set_many(obj, lang, mapping):
    for field, text in mapping.items():
        set_loc(obj, lang, field, text)

def localize_service_cta(cta):
    set_many(cta, "ar", {"title": "هل تحتاج إلى دعم لهذا العمل؟", "subtitle": "تواصل مع SESCCO لمناقشة متطلبات مشروعك.", "button_text": "اطلب عرضاً"})
    set_many(cta, "zh-hans", {"title": "需要此项工作的支持？", "subtitle": "请联系 SESCCO 讨论您的项目需求。", "button_text": "获取报价"})

def localize_project_cta(cta):
    set_many(cta, "ar", {"title": "هل لديك مشروع مشابه؟", "subtitle": "تواصل مع SESCCO لمناقشة متطلباتك الهندسية أو التعاقدية.", "button_text": "ابدأ مشروعاً"})
    set_many(cta, "zh-hans", {"title": "需要类似项目支持？", "subtitle": "请联系 SESCCO 讨论您的工程或承包需求。", "button_text": "启动项目"})

def clean(model, values):
    valid = {f.name for f in model._meta.fields}
    return {k: v for k, v in values.items() if k in valid}


def up(model, lookup, **defaults):
    obj, _ = model.objects.update_or_create(**lookup, defaults=clean(model, defaults))
    return obj


def p(*items):
    return ''.join(f'<p>{x}</p>' for x in items if x)



def attach_seed_file(instance, field_name, relative_path, target_name=None):
    """Attach a bundled seed asset to a FileField/ImageField when available."""
    source = Path(settings.BASE_DIR) / relative_path
    if not source.exists():
        return
    field = getattr(instance, field_name)
    target_name = target_name or source.name
    current_name = getattr(field, 'name', '') or ''
    if current_name.endswith(target_name):
        return
    if field and hasattr(field, 'delete'):
        try:
            field.delete(save=False)
        except Exception:
            pass
    with source.open('rb') as fh:
        field.save(target_name, File(fh), save=False)
    instance.save(update_fields=[field_name])



def attach_project_gallery(project, hero_relative_path, slideshow_relative_paths):
    """
    Attach optimized bundled project media to the project's cover image and gallery.
    This is intentionally idempotent: reseeding updates the same captioned gallery
    records instead of creating duplicates. Non-seed admin uploads are left intact.
    """
    if hero_relative_path:
        attach_seed_file(project, 'cover_image', hero_relative_path, f"{project.slug}-hero.webp")

    filtered_paths = [path for path in slideshow_relative_paths if path and path != hero_relative_path]
    for order, relative_path in enumerate(filtered_paths, 1):
        source = Path(settings.BASE_DIR) / relative_path
        if not source.exists():
            continue
        caption = f"Seed gallery {order:02d}"
        gallery_item, _ = ProjectImage.objects.update_or_create(
            project=project,
            caption=caption,
            defaults={
                "sort_order": order,
                "is_active": True,
            },
        )
        target_name = f"{project.slug}-{order:02d}.webp"
        current_name = getattr(gallery_item.image, "name", "") or ""
        if not current_name.endswith(target_name):
            if gallery_item.image and hasattr(gallery_item.image, "delete"):
                try:
                    gallery_item.image.delete(save=False)
                except Exception:
                    pass
            with source.open("rb") as fh:
                gallery_item.image.save(target_name, File(fh), save=False)
        gallery_item.sort_order = order
        gallery_item.is_active = True
        gallery_item.save(update_fields=["image", "sort_order", "is_active", "caption"])



def clear_seeded_project_media(project):
    """
    Remove only media previously attached by the seed command.
    This prevents old cross-project seed images from staying after a stricter
    media map, while leaving manual admin uploads intact.
    """
    seed_caption_prefix = "Seed gallery "
    ProjectImage.objects.filter(project=project, caption__startswith=seed_caption_prefix).delete()
    expected_seed_cover_suffix = f"{project.slug}-hero.webp"
    if project.cover_image and (project.cover_image.name or "").endswith(expected_seed_cover_suffix):
        try:
            project.cover_image.delete(save=False)
        except Exception:
            pass
        project.cover_image = None
        project.save(update_fields=["cover_image"])


def update_or_create(model, lookup=None, defaults=None, **kwargs):
    """
    Small safe wrapper used by the seed command.
    Keeps seed data idempotent and prevents duplicate records.
    """
    lookup = lookup or kwargs
    defaults = defaults or {}
    obj, _ = model.objects.update_or_create(**lookup, defaults=defaults)
    return obj


class Command(BaseCommand):
    help = 'Populate production-grade English CMS content for SESCCO.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO('Seeding SESCCO English CMS content...'))

        company = up(CompanyProfile, {'id': 1},
            company_name='Summit Engineering Solutions Cont. Co.', short_name='SESCCO',
            tagline='Where Quality Engineering Meets Dependable Service.', established_year=2015,
            aramco_vendor_code='10114560', sec_vendor_code='02013075',
            phone_primary='', phone_secondary='',
            email_primary='info@sescco.com', email_secondary='imran@sescco.com', email_third='mehrab@sescco.com',
            address='Dammam, Eastern Province, Kingdom of Saudi Arabia', city='Dammam', country='Saudi Arabia', website_url='https://sescco.com',
            description=p('Summit Engineering Solutions Cont. Co. specializes in reliable engineering, construction and contract support services across Saudi Arabia.', 'With years of experience and a commitment to excellence, SESCCO ensures that projects meet high standards of safety, efficiency and quality.', 'Core capabilities include electrical engineering services, civil and architectural fit-out works, contract support services and electromechanical works.'))

        up(SiteSettings, {'site_name': 'SESCCO'}, domain='sescco.com', default_language='en', enable_multilingual=True, default_seo_title='SESCCO | Summit Engineering Solutions Cont. Co.', default_seo_description='SESCCO provides electrical engineering, civil, architectural, fit-out, mechanical and contract support services in Saudi Arabia.', footer_social_title='Find us on social media', show_developer_credit=True, developer_credit_label='Website developed by', developer_name='A2TDEV', developer_url='https://a2tdev.com', developer_seo_description='A2TDEV is the website design and development partner for SESCCO.')
        up(ThemeSettings, {'id': 1}, primary_color='#0758d8', secondary_color='#042a5f', accent_color='#00a6df', dark_color='#061a34', light_color='#f4f8fd', header_style='standard', footer_style='standard', button_style='rounded')

        # Career module replaces the old public Downloads page in the main navigation.
        NavigationMenu.objects.filter(title__iexact='Downloads').update(is_active=False)
        NavigationMenu.objects.filter(url__in=['/downloads/', '/downloads']).update(is_active=False)
        # The public certificates page is temporarily hidden from navigation.
        NavigationMenu.objects.filter(url__in=['/clients-certifications/', '/clients-certifications']).update(is_active=False)
        for order, (title, url) in enumerate([('Home','/'),('About Us','/about/'),('Services','/services/'),('Projects','/projects/'),('Careers','/careers/'),('Contact','/contact/')], 1):
            up(NavigationMenu, {'title': title}, url=url, sort_order=order, is_active=True)

        FooterLink.objects.filter(url__in=['/clients-certifications/', '/clients-certifications']).update(is_active=False)

        up(CTASettings, {'id': 1}, header_cta_text='Get in Touch', header_cta_url='/contact/', main_cta_title='Let’s Build Something Great Together', main_cta_subtitle='Reach out to us for project inquiries, collaborations or support. We’ll get back to you promptly.', main_cta_button_text='Contact Our Team', main_cta_button_url='/contact/')
        cols = {'Company': [('About Us','/about/'),('Projects','/projects/'),('Careers','/careers/')], 'Services': [('Electrical Engineering','/services/electrical-engineering-services/'),('Civil & Fitout Works','/services/civil-architectural-fitout-works/'),('Telecommunication Services','/services/telecommunication-services/'),('Contract Support','/services/contract-support-service/')], 'Contact': [('Contact Us','/contact/'),('Open Jobs','/careers/'),('Contact HR','/contact/?type=career')]}
        for i,(col,links) in enumerate(cols.items(), 1):
            c=up(FooterColumn, {'title': col}, sort_order=i, is_active=True)
            for j,(t,u) in enumerate(links, 1): up(FooterLink, {'column': c, 'title': t}, url=u, sort_order=j, is_active=True)
        up(SocialLink, {'title': 'Website'}, url='https://sescco.com', icon_text='🌐', sort_order=1, is_active=True)

        for order,(title,value,desc,icon) in enumerate([
            ('Saudi Arabia Based','Dammam, KSA','Operating from the Eastern Province.','📍'),('Established','2015','Serving clients with dependable engineering support.','▣'),('SEC Vendor Code','02013075','Registered vendor for Saudi Electricity Company.','🛡'),('Aramco Vendor Code','10114560','Registered vendor code for Saudi Aramco.','✦'),('Trusted Clients','29+','Relationships built through performance.','👥'),('Certifications','6+','Quality, environmental and safety compliance focus.','✓')], 1):
            up(TrustMetric, {'title': title}, value=value, description=desc, icon_text=icon, sort_order=order, is_active=True, show_on_home=True, show_on_about=True)

        home=up(Page, {'slug':'home'}, title='Home', template_type='home', hero_title='Where Quality Engineering Meets Dependable Service.', hero_subtitle='SESCCO delivers integrated engineering, construction and technical solutions across Saudi Arabia with safety, quality and integrity at the core.', body='', seo_title='SESCCO | Quality Engineering & Dependable Service', seo_description='Summit Engineering Solutions Cont. Co. delivers electrical engineering, civil works, architectural fit-out and contract support services in Saudi Arabia.', is_published=True)
        about=up(Page, {'slug':'about'}, title='About Us', template_type='about', hero_title='About Summit Engineering Solutions', hero_subtitle='A Saudi-based contracting company delivering integrated engineering, construction and support services.', body=p('At Summit Engineering Solutions, we pride ourselves on being a reliable partner in achieving project goals.', 'We specialize in electrical engineering services, civil and architectural fit-out works, electromechanical works and contract support services.', 'Business activities extend across HVAC systems, fire detection and alarm systems, plumbing and sanitary works, fire suppression systems, building lighting and power systems.'), seo_title='About SESCCO | Summit Engineering Solutions', seo_description='Learn about SESCCO, a Saudi contracting company providing engineering, civil, architectural, fit-out and contract support services.', is_published=True)
        attach_seed_file(about, 'hero_image', 'static/img/seed/page-heroes/business_collaboration_with_industrial_views.webp', 'about-hero.webp')
        up(HomeHero, {'id':1}, title='Where Quality Engineering Meets Dependable Service.', subtitle='SESCCO delivers integrated engineering, construction and technical solutions across Saudi Arabia with safety, quality and integrity at the core.', primary_button_text='Our Services', primary_button_url='/services/', secondary_button_text='View Our Projects', secondary_button_url='/projects/', sphere_auto_speed=0.24, sphere_scroll_speed=0.03, sphere_settle_seconds=10.0, sphere_max_boost=0.55, is_active=True)
        up(HomeAboutBlock, {'id':1}, eyebrow='About SESCCO', title='Engineering solutions built on trust.', body=p('Summit Engineering Solutions Cont. Co. specializes in providing top-notch services across various domains.', 'With years of experience and a commitment to excellence, we ensure that all projects meet high standards of safety, efficiency and quality.', 'We build relationships with clients, employees and subcontractors on a foundation of trust and respect.'), button_text='Learn More About Us', button_url='/about/', is_active=True)
        up(HomeSectionSettings, {'id':1}, services_eyebrow='Our Services', services_title='Integrated engineering capabilities for demanding projects.', projects_eyebrow='Project Experience', projects_title='Proven experience across electrical, civil and fit-out works.', clients_eyebrow='Trusted Clients', certificates_eyebrow='Certifications & Compliance', why_choose_eyebrow='Why Choose SESCCO', why_choose_title='A dependable partner for quality, safety and execution.', show_services=True, show_projects=True, show_clients=True, show_certificates=False, show_why_choose=True)
        up(AboutPageSettings, {'id':1}, page=about, overview_eyebrow='Company Overview', overview_title='Reliable engineering and contracting partner.', mission_section_title='Mission, Vision and Values', timeline_eyebrow='Our Journey', strengths_eyebrow='Our Strengths', strengths_title='Built for dependable project delivery.', show_trust_strip=True, show_overview=True, show_mission_vision=True, show_timeline=True, show_strengths=True, show_leadership=False, show_stats=True, show_faqs=True)

        mission_items = [
            ('Mission', 'mission', '◎', 'To deliver dependable engineering, construction and technical support solutions through safe execution, disciplined workmanship and practical project control.'),
            ('Vision', 'vision', '◉', 'To be recognized across Saudi Arabia as a trusted engineering partner known for reliability, quality performance and long-term client value.'),
        ]
        for order, (title, item_type, icon, desc) in enumerate(mission_items, 1):
            up(MissionVisionItem, {'title': title}, page=about, item_type=item_type, icon_text=icon, description=desc, sort_order=order, is_active=True)
        value_items = [
            ('Trust & Respect', '✓', 'We keep our promises, communicate clearly and build relationships on accountability, professionalism and respect.'),
            ('Safe Workplace', '✓', 'We protect people, sites and the environment through safe work practices and responsible supervision.'),
            ('Quality Execution', '✓', 'We focus on reliable delivery, proper documentation and workmanship that meets project requirements.'),
        ]
        for order, (title, icon, desc) in enumerate(value_items, 1):
            up(ValueItem, {'title': title}, page=about, icon_text=icon, description=desc, sort_order=order, is_active=True)
        leadership = up(LeadershipMessage, {'id':1}, page=about, title='A Message from Managing Committee', message=p('At Summit Engineering Solutions Cont. Co., our progress is built on disciplined execution, technical responsibility, and a commitment to safety, quality, and long-term client trust. We approach every project with precision and purpose—delivering engineering solutions that meet the highest standards and create lasting value for our clients, our people, and the communities we serve.', 'Quality is at the core of everything we do. From rigorous planning to meticulous execution, we uphold robust systems and industry best practices to ensure reliable, efficient, and safe outcomes. Our teams are empowered to take ownership, solve complex challenges, and drive continuous improvement in every phase of our work.', 'We believe trust is earned through transparency, accountability, and performance. By fostering strong partnerships and maintaining open communication, we build relationships that stand the test of time and support our shared success.', 'As a managing committee, we remain committed to strengthening our capabilities, investing in our people and technologies, and delivering solutions that contribute to the Kingdom’s growth and sustainable industrial future.'), person_name='Managing Committee', person_designation='Summit Engineering Solutions Cont. Co.', is_active=True, sort_order=1)
        if not leadership.background_image:
            attach_seed_file(leadership, 'background_image', 'static/img/seed/leadership/managing-committee-bg.svg', 'managing-committee-bg.svg')
        for order,(year,title,desc) in enumerate([('2015','Foundation','SESCCO was established to deliver dependable engineering and contracting services.'),('2021','Major Civil Works','Participation in industrial civil and infrastructure works.'),('2023','Pipeline Experience','Execution support for ROW, trench excavation, backfilling and berming works.'),('2025','Expanded Project Portfolio','Continued delivery across electrical, civil, fit-out and contract support projects.')],1): up(TimelineItem, {'year':year,'title':title}, page=about, description=desc, sort_order=order, is_active=True)
        for order,(label,value) in enumerate([('Years of Trust','10+'),('Vendor Codes','2'),('Core Service Areas','5'),('Project Categories','4')],1): up(StatItem, {'label':label}, page=about, value=value, sort_order=order, is_active=True)
        for order,(title,desc) in enumerate([('Safety-Focused Execution','We prioritize safe work practices and reliable site execution.'),('Skilled Workforce','Qualified personnel capable of supporting complex requirements.'),('Flexible Contract Support','Scalable project-team and equipment support according to project needs.'),('Quality Commitment','Work guided by quality, efficiency and client satisfaction.')],1): up(WhyChooseItem, {'title':title}, description=desc, icon_text='✓', sort_order=order, is_active=True)

        service_page_settings = up(ServiceListPageSettings, {'id':1}, eyebrow='Services', hero_title='Our Services', hero_subtitle='Comprehensive engineering solutions delivered with expertise, quality and a commitment to excellence.', intro_title='Practical services for reliable execution.', intro_text=p('Our service model supports safe, efficient and high-quality project delivery across Saudi Arabia.'), show_category_tabs=False)
        attach_seed_file(service_page_settings, 'hero_image', 'static/img/seed/page-heroes/on_site_engineering_team_discussion.webp', 'services-hero.webp')
        service_cats={}
        category_seed=[
            ('Electrical Engineering','Design, installation, maintenance and troubleshooting for electrical systems.','⚡'),
            ('Civil & Architectural Fitout','Civil construction, infrastructure support, architectural and fit-out works.','▥'),
            ('Contract Support','Qualified workforce, equipment support and flexible project-team solutions.','👥'),
            ('Telecommunication Services','Network, cabling, cabinet, fiber and communication infrastructure support.','◌'),
            ('Electromechanical Works','HVAC, fire systems, plumbing, lighting, power and related building services.','⚙'),
            ('Mechanical & Fire Fighting','Mechanical installations and fire-fighting system works.','♨'),
        ]
        for order,(name,desc,icon) in enumerate(category_seed,1):
            service_cats[name]=up(ServiceCategory, {'slug':slugify(name)}, name=name, icon_text=icon, description=desc, sort_order=order, is_active=True)
        service_data=[
            ('Electrical Engineering Services','Electrical Engineering','Comprehensive design, installation, maintenance and troubleshooting for electrical systems.','⚡','static/img/seed/services/electrical-engineering-services.webp',['GIS, transformer and panel installation','MV/LV cable laying and termination','Protection, control and SAS panel works','Lighting and power systems']),
            ('Civil, Architectural & Fitout Works','Civil & Architectural Fitout','Construction, infrastructure development, maintenance, architectural works and professional fit-out delivery.','▥','static/img/seed/services/civil-architectural-fitout-works.webp',['Rebar binding, shuttering and concreting','Plastering, painting, screed and tiles','Office, villa and industrial fit-out','Civil construction and infrastructure works']),
            ('Contract Support Service','Contract Support','Skilled workforce and equipment support for project execution with flexible resources.','👥','static/img/seed/services/contract-support-service.webp',['Qualified personnel','Flexible project-team support','Motorized vehicles and equipment','Improved project productivity']),
            ('Telecommunication Services','Telecommunication Services','Network, cabling, cabinet, fiber and communication infrastructure support for project sites and facilities.','◌','static/img/hero_sphere/optimized/batch2_05_telecom_infrastructure.webp',['Fiber and network cable works','Telecommunication cabinet support','OPGW and communication infrastructure','Testing and coordination support']),
            ('Electromechanical Works','Electromechanical Works','Integrated electromechanical works covering HVAC, fire systems, plumbing and building utilities.','⚙','static/img/seed/services/electromechanical-works.webp',['HVAC systems','Fire detection and alarm systems','Plumbing and sanitary works','Fire suppression systems','Building lighting and power systems']),
            ('Mechanical & Fire-Fighting Systems','Mechanical & Fire Fighting','Mechanical and fire-fighting installations for industrial facilities and warehouses.','♨','static/img/seed/services/mechanical-fire-fighting-systems.webp',['Fire-fighting system installation','Mechanical installation support','Testing and commissioning support']),
        ]
        for order,(title,cat,desc,icon,image_path,points) in enumerate(service_data,1):
            svc=up(Service, {'slug':slugify(title)}, category=service_cats[cat], title=title, short_description=desc, body=p(desc,'SESCCO supports this service with skilled personnel, safe work practices and dependable execution.'), icon_text=icon, sort_order=order, is_featured=True, is_active=True, seo_title=f'{title} | SESCCO', seo_description=desc)
            attach_seed_file(svc, 'cover_image', image_path, f"service-{slugify(title)}.webp")
            for j,point in enumerate(points,1):
                up(ServiceKeyPoint, {'service':svc,'title':point}, description=point, icon_text='✓', sort_order=j, is_active=True)
                up(ServiceDeliverable, {'service':svc,'title':point}, description=point, icon_text='▣', sort_order=j, is_active=True)
            for j,(step,sd) in enumerate([('Requirement Review','Review project scope, site needs and technical requirements.'),('Planning & Mobilization','Prepare resources, equipment and execution planning.'),('Execution & Quality Control','Complete work with safety coordination and quality checks.'),('Handover & Support','Provide project close-out support and documentation where required.')],1): up(ServiceProcessStep, {'service':svc,'title':step}, step_number=j, description=sd, icon_text=str(j), sort_order=j, is_active=True)
            feature_seed = [
                ('Safety-led delivery', 'Work is planned and executed with site safety, permit coordination and quality control in mind.', '🛡'),
                ('Experienced workforce', 'SESCCO mobilizes trained personnel familiar with industrial, utility and commercial project environments.', '👷'),
                ('Documentation support', 'Progress, inspection and close-out information can be supported according to project requirements.', '📄'),
            ]
            for j,(feature_title, feature_desc, feature_icon) in enumerate(feature_seed,1):
                up(ServiceFeature, {'service':svc,'title':feature_title}, description=feature_desc, icon_text=feature_icon, sort_order=j, is_active=True)
            faq_seed = [
                ('What does this SESCCO service cover?', f'{title} covers {desc.lower()} SESCCO can align the final scope with the client requirement, site condition and project schedule.'),
                ('Can SESCCO support projects outside Dammam?', 'Yes. SESCCO can support projects across Saudi Arabia subject to project scope, location, resource requirements and mobilization plan.'),
                ('Can personnel and equipment be arranged for this service?', 'Yes. SESCCO can provide qualified personnel and project support resources according to approved requirements and availability.'),
                ('How can I request a quotation?', 'Use the contact form or request-a-quote button and share the project location, required scope, timeline, drawings or any available technical information.'),
            ]
            for j,(question, answer) in enumerate(faq_seed,1):
                up(ServiceFAQ, {'service':svc,'question':question}, answer=p(answer), sort_order=j, is_active=True)
            service_cta = up(ServiceCTA, {'service':svc}, title=f'Need support with {title.lower()}?', subtitle='Contact SESCCO to discuss your project requirements.', button_text='Request a Quote', button_url='/contact/', is_active=True)
            localize_service_cta(service_cta)

        service_list_faqs = [
            ('What are SESCCO’s main service areas?', 'SESCCO provides electrical engineering services, civil and architectural fit-out works, contract support services, electromechanical works, HVAC, fire systems, plumbing, sanitary works, lighting and power systems.'),
            ('Does SESCCO handle both engineering and execution support?', 'Yes. SESCCO supports clients with technical execution, skilled workforce, equipment support and coordinated site delivery according to project needs.'),
            ('Can SESCCO provide service information before a quotation?', 'Yes. The team can review the requirement and guide the client on capability, availability and the information needed to prepare a quotation.'),
            ('Which sectors does SESCCO support?', 'SESCCO supports industrial, utility, infrastructure, commercial and building-related projects across Saudi Arabia.'),
        ]
        for order,(question, answer) in enumerate(service_list_faqs,1):
            up(ServiceListFAQ, {'question':question}, answer=p(answer), sort_order=order, is_active=True)
        for order,(title, description, icon) in enumerate([
            ('Requirement review', 'We review scope, drawings, schedule and site needs before execution.', 'review'),
            ('Resource planning', 'We plan project teams, equipment and coordination requirements.', 'planning'),
            ('Safe execution', 'Work is executed with safety, quality and client coordination.', 'execution'),
            ('Close-out support', 'We support handover, records and follow-up where required.', 'closeout'),
        ],1):
            up(ServiceListProcessStep, {'title':title}, description=description, icon_text=icon, sort_order=order, is_active=True)

        up(ServiceDetailPageSettings, {'id': 1}, default_hero_eyebrow='Service Detail', show_key_points=True, show_deliverables=True, show_features=True, show_process=True, show_related_projects=True, show_brochure=True, show_faqs=True)
        up(ProjectDetailPageSettings, {'id': 1}, default_hero_eyebrow='Project Case Study', show_summary=True, show_quick_facts=True, show_gallery=True, show_case_study_blocks=True, show_metrics=True, show_documents=True, show_related_projects=True, show_cta=True)

        project_page_settings = up(ProjectListPageSettings, {'id':1}, eyebrow='Project Experience', hero_title='Proven Project Experience Across Saudi Arabia', hero_subtitle='SESCCO’s portfolio includes electrical, civil, architectural fit-out, pipeline, mechanical and support projects.', intro_title='Experience that reflects execution capability.', intro_text=p('Our project experience demonstrates the ability to work across industrial, utility and commercial environments.'), show_category_tabs=True)
        attach_seed_file(project_page_settings, 'hero_image', 'static/img/seed/page-heroes/industrial_construction_site_with_city_skyline.webp', 'projects-hero.webp')
        pcats={}
        for order,(name,desc) in enumerate([('Electrical Projects','Electrical substations, cable works, switchgear and testing projects.'),('Civil Projects','Civil construction, infrastructure and pipeline-related works.'),('Architectural & Fitout Projects','Office, villa, commercial and industrial fit-out projects.'),('Mechanical Projects','Mechanical and fire-fighting system project experience.')],1): pcats[name]=up(ProjectCategory, {'slug':slugify(name)}, name=name, description=desc, sort_order=order, is_active=True)
        projects=[
            ('Replacement of Existing Outdoor Aindar Sub-30 with New GIS Substation','Electrical Projects','Saudi Electricity Company','Abahsain Consolidated Co.','Saudi Arabia','completed',2025,'6 Months (June 2025)','Installation of GIS, power transformer, protection, control and SAS panels including cable laying and termination.'),
            ('Yanbu 4 - 110kV HV Substation Interface Works','Electrical Projects','Saudi Water Company','Energy & Power Cont. Co.','Yanbu, Saudi Arabia','completed',2026,'7 Months (April 2026)','Installation of power transformer, cable tray, MDP, lighting panel, generator, MV/LV cable laying and cable termination.'),
            ('Replacement of 13.8kV SWGR','Electrical Projects','NG/SEC','Abahsain Consolidated Co.','Jubail, Saudi Arabia','completed',2025,'Project Completed','Replacement of existing 13.8kV switchgear with new SIEMENS SF6 switchgear including LV power/control cable and 13.8kV power cable termination.'),
            ('MV Cable Fault Location Test, Damage Repair and Termination','Electrical Projects','SEPCO','SESCCO Team','Jafurah, Saudi Arabia','ongoing',2025,'8 Months (April 2025)','Fault location testing, splicing, insulation repair, termination and high-potential testing of underground MV cable.'),
            ('EPCC 10,000TPD Clinker Cement Plant Civil Works','Civil Projects','Industrial Client','SINOMA','Saudi Arabia','completed',2025,'8 Months (May 2025)','Civil works including rebar binding, shuttering and concreting for additive crusher areas, transfer foundations, clinker silo and gallery area.'),
            ('EPCC 10,000TPD Clinker Cement Plant Architectural & Fitout Works','Architectural & Fitout Projects','Industrial Client','SINOMA','Saudi Arabia','completed',2025,'6 Months (July 2025)','Finishing works including block laying, tie beam, plastering, painting, screed, tiles and gypsum works.'),
            ('Roshan Ewan Sedra 2 Villas Tile Works','Architectural & Fitout Projects','Roshan','SESCCO Team','Riyadh, Saudi Arabia','completed',2025,'Completed May 2025','Porcelain wall, bathroom and floor tile works, plus marble stair tiles for 21 villas.'),
            ('Haradh RTR Pipeline Project','Civil Projects','Industrial Client','SESCCO Team','Haradh, Saudi Arabia','completed',2023,'12 Months (Completed June 2023)','ROW preparation, trench excavation, backfilling and berming for a 130 km pipeline project.'),
            ('Jafurah Upstream Pipeline Project','Civil Projects','Industrial Client','SESCCO Team','Jafurah, Saudi Arabia','completed',2024,'18 Months (Completed October 2024)','12-inch and 14-inch RTR pipe lowering and installation, trench excavation, backfilling and berming for a 175 km project.'),
            ('McDermott Arabia Office Fitout','Architectural & Fitout Projects','McDermott Arabia','SESCCO Team','Al Khobar, Saudi Arabia','completed',2016,'Completed October 2016','Structural and complete office fit-out works covering approximately 7,000 sqm.'),
            ('Worley Parsons Office Fitout','Architectural & Fitout Projects','Worley Parsons','SESCCO Team','Al Khobar, Saudi Arabia','completed',2016,'Completed August 2016','Complete office fit-out works covering approximately 16,800 sqm.'),
            ('Fire-Fighting System Installation for Industrial Facility and Warehouse','Mechanical Projects','ARAMCO','EPC','Saudi Arabia','completed',2025,'Completed','Installation of fire-fighting systems for an industrial facility and warehouse.'),
            ('Ethernet Cable Installation and Testing Works','Electrical Projects','Industrial Client','SESCCO Team','Saudi Arabia','completed',2025,'Completed','Ethernet cable preparation, installation, labeling and testing support for low-current project requirements.'),
            ('Telecommunication Cabinet and Network Support Works','Electrical Projects','SEPCO','SESCCO Team','Saudi Arabia','completed',2025,'Completed','Telecommunication cabinet, panel and network support works with site coordination and quality checks.'),
            ('SEPCO Telecommunication Field Support Works','Electrical Projects','SEPCO','SESCCO Team','Saudi Arabia','completed',2025,'Completed','Telecommunication field support, inspection assistance and installation coordination for project delivery.'),
            ('OPGW Fiber Splicing and Testing Works','Electrical Projects','SEPCO','SESCCO Team','Saudi Arabia','completed',2025,'Completed','OPGW fiber splicing, testing and technical support works for telecommunication infrastructure.'),
            ('Asphalting and Site Preparation Works','Civil Projects','Industrial Client','SESCCO Team','Saudi Arabia','completed',2025,'Completed','Asphalting and site preparation support works using real project field photos from the uploaded project media set.'),
        ]
        # Remove the older combined Avenues record. The company profile lists
        # plaster and screed as separate work packages, so keeping this combined
        # project creates a duplicate/card with fallback image.
        Project.objects.filter(slug='the-avenues-khobar-plaster-and-screed-works').update(is_active=False)

        def seed_media_files(folder, *names):
            folder_path = Path(folder)
            return [
                str(folder_path / name)
                for name in names
                if (Path(settings.BASE_DIR) / folder_path / name).exists()
            ]

        # Strict project media map:
        # Only attach photos when the uploaded folder clearly belongs to that
        # project/work package. If a project does not have specific real photos,
        # leave its cover/gallery empty so the site can use the normal fallback
        # instead of borrowing another project's image.
        project_media_map = {
            'replacement-of-existing-outdoor-aindar-sub-30-with-new-gis-substation': (
                'static/img/seed/project-media/slideshow/electrical/substation/gis-01.webp',
                seed_media_files('static/img/seed/project-media/slideshow/electrical/substation', 'panel-01.webp', 'panel-02.webp', 'sas01.webp', 'termination-01.webp'),
            ),
            'yanbu-4-110kv-hv-substation-interface-works': (
                'static/img/seed/project-media/slideshow/electrical/substation/cable-tray-02.webp',
                seed_media_files('static/img/seed/project-media/slideshow/electrical/substation', 'cable-tray-01.webp', 'cable-tray-03.webp', 'termination-01.webp'),
            ),
            'mv-cable-fault-location-test-damage-repair-and-termination': (
                'static/img/seed/project-media/slideshow/mv-cable-pictures/mv-cable-splicing/mv-cable-splicing-01.webp',
                seed_media_files('static/img/seed/project-media/slideshow/mv-cable-pictures/mv-cable-splicing', 'mv-cable-splicing-00.webp', 'whatsapp-image-2025-07-08-at-5-25-31-pm.webp', 'whatsapp-image-2025-07-08-at-5-25-46-pm.webp'),
            ),
            'epcc-10000tpd-clinker-cement-plant-civil-works': (
                'static/img/seed/project-media/slideshow/civil/sinoma/civil-foundation-work/c.webp',
                seed_media_files('static/img/seed/project-media/slideshow/civil/sinoma/civil-foundation-work', '01.webp', '02.webp', '03.webp', 'a.webp'),
            ),
            'epcc-10000tpd-clinker-cement-plant-architectural-fitout-works': (
                'static/img/seed/project-media/slideshow/civil/sinoma/finishing-work/plaster.webp',
                seed_media_files('static/img/seed/project-media/slideshow/civil/sinoma/finishing-work', 'painting.webp', 'whatsapp-image-2025-07-08-at-18-01-09-53f5f542.webp', 'whatsapp-image-2025-07-08-at-18-01-10-2ae773b0.webp'),
            ),
            'the-avenues-khobar-plaster-works': (
                'static/img/seed/project-media/slideshow/civil/havelock-1/plaster-3.webp',
                seed_media_files('static/img/seed/project-media/slideshow/civil/havelock-1', 'plaster-1.webp', 'plaster-2.webp', 'plaster-4.webp'),
            ),
            'the-avenues-khobar-screed-works': (
                'static/img/seed/project-media/slideshow/civil/havelock-1/screed-3.webp',
                seed_media_files('static/img/seed/project-media/slideshow/civil/havelock-1', 'screed-1.webp', 'screed-2.webp', 'screed-4.webp'),
            ),
            'preparation-and-painting-of-230kv-ohtl-foundation': (
                'static/img/seed/project-media/slideshow/civil/sepco/paint-2.webp',
                seed_media_files('static/img/seed/project-media/slideshow/civil/sepco', 'paint-1.webp', 'paint-3.webp', 'paint-4.webp'),
            ),
            'dismantling-and-transportation-of-tfc-at-haradh': (
                'static/img/seed/project-media/slideshow/civil/tr/tr1.webp',
                seed_media_files('static/img/seed/project-media/slideshow/civil/tr', 'tr2.webp', 'tr3.webp', 'tr4.webp'),
            ),
            'fire-fighting-system-installation-for-industrial-facility-and-warehouse': (
                'static/img/seed/project-media/slideshow/fire-fighting-system/sprinkler/01.webp',
                seed_media_files('static/img/seed/project-media/slideshow/fire-fighting-system/sprinkler', '02.webp', '03.webp', '04.webp'),
            ),
            'ethernet-cable-installation-and-testing-works': (
                'static/img/seed/project-media/slideshow/ethernet-cable/whatsapp-image-2025-07-08-at-5-18-09-pm.webp',
                seed_media_files('static/img/seed/project-media/slideshow/ethernet-cable', 'whatsapp-image-2025-07-08-at-5-17-54-pm.webp', 'whatsapp-image-2025-07-08-at-5-19-12-pm.webp', 'whatsapp-image-2025-07-08-at-5-19-50-pm.webp'),
            ),
            'telecommunication-cabinet-and-network-support-works': (
                'static/img/seed/project-media/slideshow/telecommunication/old/whatsapp-image-2025-02-13-at-09-35-13-efafa2ad.webp',
                seed_media_files('static/img/seed/project-media/slideshow/telecommunication/old', 'foc-splicing-box.webp', 'cable-laid.webp', 'oip.webp'),
            ),
            'sepco-telecommunication-field-support-works': (
                'static/img/seed/project-media/slideshow/telecommunication/sepco/whatsapp-image-2025-07-08-at-4-16-28-pm.webp',
                seed_media_files('static/img/seed/project-media/slideshow/telecommunication/sepco', 'whatsapp-image-2025-07-08-at-4-15-47-pm.webp', 'whatsapp-image-2025-07-08-at-4-23-24-pm.webp', 'a.webp'),
            ),
            'opgw-fiber-splicing-and-testing-works': (
                'static/img/seed/project-media/slideshow/telecommunication/sepco/opgw/opgw2.webp',
                seed_media_files('static/img/seed/project-media/slideshow/telecommunication/sepco/opgw', 'opgw1.webp', 'opgw3.webp', 'opgw4.webp'),
            ),
            'asphalting-and-site-preparation-works': (
                'static/img/seed/project-media/slideshow/asphalting/whatsapp-image-2025-02-13-at-09-33-11-81a64ca0.webp',
                seed_media_files('static/img/seed/project-media/slideshow/asphalting', 'whatsapp-image-2025-02-13-at-09-33-09-4836dd36.webp', 'whatsapp-image-2025-02-13-at-09-33-10-c046010b.webp', 'whatsapp-image-2025-02-13-at-09-33-21-27b12d28.webp'),
            ),
        }
        for order,(title,cat,client,contractor,loc,status,year,duration,summary) in enumerate(projects,1):
            pr=up(Project, {'slug':slugify(title)}, category=pcats[cat], title=title, client_name=client, contractor_name=contractor, location=loc, status=status, year=year, duration=duration, short_description=summary, summary=p(summary), challenge=p('The project required safe execution, technical coordination and dependable site productivity.'), scope=p(summary), solution=p('SESCCO supported the works through skilled teams, organized execution and quality-focused delivery.'), outcomes=p('The project contributed to client objectives while reflecting SESCCO’s commitment to quality and safety.'), sort_order=order, is_featured=order<=6, is_active=True, seo_title=f'{title} | SESCCO Project Experience', seo_description=summary[:250])
            media_config = project_media_map.get(pr.slug)
            if media_config:
                hero_path, gallery_config = media_config
                if isinstance(gallery_config, (list, tuple)):
                    gallery_paths = list(gallery_config)
                else:
                    gallery_source = Path(settings.BASE_DIR) / gallery_config
                    gallery_paths = []
                    if gallery_source.exists():
                        gallery_paths = [
                            str(Path(gallery_config) / file.name)
                            for file in sorted(gallery_source.glob("*.webp"))
                        ]
                attach_project_gallery(pr, hero_path, gallery_paths)
            else:
                clear_seeded_project_media(pr)
            for j,(label,value) in enumerate([('Location',loc),('Status',status.title()),('Duration',duration),('Contractor',contractor)],1): up(ProjectMetric, {'project':pr,'label':label}, value=value, icon_text='•', sort_order=j, is_active=True)
            project_cta = up(ProjectCTA, {'project':pr}, title='Need a similar project partner?', subtitle='Contact SESCCO to discuss your engineering or contracting requirements.', button_text='Start a Project', button_url='/contact/', is_active=True)
            localize_project_cta(project_cta)
        for order,(label,value) in enumerate([('Electrical Projects','8+'),('Civil Projects','7+'),('Fitout Projects','6+'),('Core Clients','10+')],1): up(ProjectListStat, {'label':label}, value=value, icon_text='▣', sort_order=order, is_active=True)

        trust_page_settings = up(TrustPageSettings, {'id':1}, eyebrow='Clients', hero_title='Clients and project references.', hero_subtitle='Review the client organizations connected to SESCCO project experience.', clients_eyebrow='Our Key Clients', clients_title='Trusted by respected organizations.', partners_eyebrow='Project Network', partners_title='Project contractors only for project detail records.', certificates_eyebrow='Our Certifications', certificates_title='Certified systems and operational excellence.', standards_eyebrow='Compliance & Standards', standards_title='Standards that guide our work.', testimonials_eyebrow='Client Feedback', testimonials_title='What clients say about SESCCO.', show_clients=True, show_partners=False, show_certificates=False, show_accreditations=True, show_standards=True, show_testimonials=True, show_documents=True)
        attach_seed_file(trust_page_settings, 'hero_image', 'static/img/seed/page-heroes/engineering_collaboration_in_a_high_tech_room.webp', 'clients-hero.webp')
        ind=up(ClientCategory, {'slug':'industrial-clients'}, name='Industrial Clients', description='Major industrial, utility and infrastructure clients.', sort_order=1, is_active=True)

        # Upgrade 114: replace the old sample clients with the real client logo pack.
        # The user-provided client logos are bundled in static/img/seed/clients/ and
        # every seeded client is featured so the home marquee can show the full list.
        Client.objects.all().delete()
        seeded_clients = [
            ('Abahsain Consolidating Co.', 'static/img/seed/clients/client-abahsain-consolidating-co.png'),
            ('ABRAR', 'static/img/seed/clients/client-abrar.png'),
            ('Al Rajhi Bank', 'static/img/seed/clients/client-al-rajhi-bank.png'),
            ('ARAMCO', 'static/img/seed/clients/client-aramco.png'),
            ('BCC', 'static/img/seed/clients/client-bcc.png'),
            ('DACO', 'static/img/seed/clients/client-daco.png'),
            ('Energy & Power Cont. Co. Ltd.', 'static/img/seed/clients/client-energy-and-power-cont-co-ltd.png'),
            ('EPC', 'static/img/seed/clients/client-epc.png'),
            ('Havelock1', 'static/img/seed/clients/client-havelock1.png'),
            ('L & T', 'static/img/seed/clients/client-l-and-t.png'),
            ('McDermott', 'static/img/seed/clients/client-mcdermott.png'),
            ('MOBILY', 'static/img/seed/clients/client-mobily.png'),
            ('NHC', 'static/img/seed/clients/client-nhc.png'),
            ('Novartis', 'static/img/seed/clients/client-novartis.png'),
            ('Riyadh Airport Company', 'static/img/seed/clients/client-riyadh-airport-company.png'),
            ('Rommel Electro Arabia', 'static/img/seed/clients/client-rommel-electro-arabia.png'),
            ('Royal Comision', 'static/img/seed/clients/client-royal-comision.png'),
            ('SABIC', 'static/img/seed/clients/client-sabic.png'),
            ('SAIPEM', 'static/img/seed/clients/client-saipem.png'),
            ('Saudi Energy', 'static/img/seed/clients/client-saudi-energy.png'),
            ('Saudi National Bank', 'static/img/seed/clients/client-saudi-national-bank.png'),
            ('SEC', 'static/img/seed/clients/client-sec.png'),
            ('SEPCO', 'static/img/seed/clients/client-sepco.png'),
            ('Seven Entertainment Ventures', 'static/img/seed/clients/client-seven-entertainment-ventures.png'),
            ('SINOMA', 'static/img/seed/clients/client-sinoma.png'),
            ('STC', 'static/img/seed/clients/client-stc.png'),
            ('TR', 'static/img/seed/clients/client-tr.png'),
            ('Worley Parsons', 'static/img/seed/clients/client-worley-parsons.png'),
            ('ZAIN', 'static/img/seed/clients/client-zain.png'),
        ]
        for order, (name, logo_path) in enumerate(seeded_clients, 1):
            client = up(Client, {'name': name}, category_ref=ind, category='Client / Project Stakeholder', description='A trusted organization connected to SESCCO’s project and delivery network.', sort_order=order, is_active=True, is_featured=True)
            attach_seed_file(client, 'logo', logo_path, f"client-{slugify(name)}.png")
        for order,name in enumerate(['Energy & Power Contracting Co.','Abahsain Consolidated Co.','Rommel Electro Arabia','Future Technologies'],1):
            up(Partner, {'name':name}, partner_tier='Contractor / Client', sort_order=order, is_active=True, is_featured=True)
        cc=up(CertificateCategory, {'slug':'iso-certifications'}, name='ISO Certifications', description='Quality, environmental, health & safety and cybersecurity compliance certifications.', sort_order=1, is_active=True)
        seeded_certificates = [
            (
                'ISO 9001',
                'Quality Management',
                'Quality management system certification for engineering, procurement, construction, testing and commissioning services.',
                'SCK Certifications Pvt. Ltd.',
                'static/img/seed/certificates/iso-9001.webp',
                'certificate-iso-9001.webp',
            ),
            (
                'ISO 14001',
                'Environmental Management',
                'Environmental management system certification reflecting responsible operational and site coordination practices.',
                'SCK Certifications Pvt. Ltd.',
                'static/img/seed/certificates/iso-14001.webp',
                'certificate-iso-14001.webp',
            ),
            (
                'ISO 45001',
                'Occupational Health & Safety',
                'Occupational health and safety management certification supporting safer workplaces and disciplined project execution.',
                'SCK Certifications Pvt. Ltd.',
                'static/img/seed/certificates/iso-45001.webp',
                'certificate-iso-45001.webp',
            ),
            (
                'Cybersecurity Compliance',
                'Cybersecurity Compliance Certificate',
                'Saudi Aramco third-party cybersecurity compliance certificate assessed against the SACS-002 standard.',
                'Seven Technologies - Saudi Arabia',
                'static/img/seed/certificates/cybersecurity-compliance-certificate.webp',
                'certificate-cybersecurity-compliance.webp',
            ),
        ]
        for order, (title, ctype, desc, issuer, image_path, target_name) in enumerate(seeded_certificates, 1):
            cert = up(Certificate, {'title': title}, category_ref=cc, certificate_type=ctype, description=desc, issuer=issuer, sort_order=order, is_active=True, is_featured=True)
            attach_seed_file(cert, 'image', image_path, target_name)
        # Keep accreditations and standards separate so the Trust Framework section
        # does not repeat the same cards on both sides. Accreditations are vendor/
        # registration credentials; standards are operating management commitments.
        for order,(title,desc) in enumerate([
            ('Saudi Aramco Vendor Code','SESCCO vendor code: 10114560.'),
            ('Saudi Electricity Company Vendor Code','SESCCO SEC vendor code: 02013075.'),
            ('Verified Compliance Records','Vendor references and supporting documents are organized for review-ready confidence.'),
        ],1):
            up(Accreditation, {'title':title}, description=desc, sort_order=order, is_active=True)
        for order,(title,desc,icon) in enumerate([
            ('Quality Management','Quality-focused execution supported by controlled processes and dependable service delivery.','✓'),
            ('Environmental Responsibility','Work practices are guided by responsible site coordination and environmental awareness.','◎'),
            ('Occupational Health & Safety','Safety-led planning, workforce awareness and site discipline support safer project execution.','盾'),
        ],1):
            up(Standard, {'title':title}, description=desc, icon_text=icon, sort_order=order, is_active=True)
        for order,(title,desc) in enumerate([('Safety','We prioritize safe work practices and protection of people and the environment.'),('Quality','We focus on meeting project requirements and client expectations.'),('Reliability','We build long-term partnerships through dependable execution.')],1): up(ComplianceBlock, {'title':title}, description=desc, icon_text='✓', sort_order=order, is_active=True)

        download_page_settings = up(DownloadsPageSettings, {'id':1}, eyebrow='Downloads', hero_title='Company Profile and Key Documents', hero_subtitle='Access company profile documents, certifications and important supporting information.', intro_title='Document Center', intro_text='Download or request SESCCO documents from the document center.', show_category_tabs=True, show_search=True, show_featured_document=True, show_document_table=True, show_request_document=True)
        attach_seed_file(download_page_settings, 'hero_image', 'static/img/seed/page-heroes/urban_construction_at_dusk.webp', 'downloads-hero.webp')
        dc=up(DocumentCategory, {'slug':'company-documents'}, name='Company Documents', icon_text='PDF', sort_order=1, is_active=True)
        document_seed = [
            ('SESCCO Company Profile', 'Official English company profile for Summit Engineering Solutions Cont. Co., including vendor codes, capabilities, services, project experience and certifications.', 'PDF', '2026.1', 'static/docs/sescco-company-profile-en.pdf'),
            ('ISO Certification Pack', 'Quality, environmental and health & safety certification references.', 'PDF', '1.0', ''),
            ('Vendor Registration Information', 'Aramco Vendor Code 10114560 and SEC Vendor Code 02013075 reference information.', 'PDF', '1.0', ''),
        ]
        for order,(title,desc,ftype,version,file_path) in enumerate(document_seed,1):
            doc=up(DownloadDocument, {'slug':slugify(title)}, category=dc, title=title, description=desc, file_type=ftype, version=version, file_size='20 MB' if file_path else '', is_featured=order==1, is_public=True, requires_request=False, access_level='public', preview_enabled=True, sort_order=order, is_active=True)
            if file_path:
                attach_seed_file(doc, 'file', file_path, 'sescco-company-profile-en.pdf')
        up(DocumentPageCTA, {'id':1}, title='Need a specific document?', subtitle='Tell us which document you need and our team will respond soon.', button_text='Request a Document', button_url='/downloads/request/', is_active=True)

        career_page_settings = up(CareerPageSettings, {'id':1}, eyebrow='Careers', hero_title='Build Your Career with SESCCO', hero_subtitle='Explore open positions, apply online and join a team committed to safe, reliable engineering execution.', hero_primary_button_text='View Open Jobs', hero_primary_button_url='#open-roles', hero_secondary_button_text='Contact HR', hero_secondary_button_url='/contact/?type=career', meta_title='Careers | SESCCO', meta_description='Explore career opportunities at SESCCO and apply online with your CV and supporting documents.', intro_eyebrow='Open Opportunities', intro_title='Find the right role for your next step', intro_text='We review every application carefully and invite shortlisted candidates for interview through official email.', empty_jobs_title='No open jobs found', empty_jobs_text='Try another search or check again later for new opportunities.', benefits_eyebrow='Why Work With Us', benefits_title='A practical environment for serious professionals', benefits_text='SESCCO career opportunities are built around project readiness, safe execution, technical growth and reliable teamwork.', process_eyebrow='Hiring Process', process_title='Simple hiring process', process_text='Apply, get reviewed, attend the interview and join the project team.', form_help_title='Before submitting', form_help_text='Prepare a clear CV and attach documents that support the role. Make sure your email and phone number are correct.', application_guide_title='Application checklist', application_guide_text='Use PDF, DOC or DOCX files only. Shortlisted applicants will receive interview details by email.', applicant_profile_title='Applicant profile', applicant_profile_text='Add your location, work authorization, experience and useful profile links so HR can review the application faster.', document_upload_title='Application documents', document_upload_text='Upload your CV and any supporting certificates, licenses or project documents as PDF, DOC or DOCX files. Multiple additional documents are supported.', duplicate_application_title='Application already submitted', duplicate_application_text='You have already applied to this post with this email. Please contact HR if you need to update your application.', privacy_notice='Your information will only be used for recruitment review and official communication about this application.', success_eyebrow='Application Submitted', success_title='Thank you for applying.', success_text='Your application has been received. Our HR team will review your CV and documents. Shortlisted applicants will receive an interview invitation by email.', show_filters=True, show_stats=True, show_benefits=True, show_process=True, show_cta=True, cta_title='Didn’t find the exact role?', cta_text='Check this page again soon or contact our HR team for future opportunities.', cta_button_text='Contact HR', cta_button_url='/contact/?type=career', recruitment_email='hr@sescco.com', email_from_name='SESCCO HR Team', email_verification_subject=DEFAULT_EMAIL_VERIFICATION_SUBJECT, email_verification_body=DEFAULT_EMAIL_VERIFICATION_BODY, interview_email_subject=DEFAULT_INTERVIEW_EMAIL_SUBJECT, interview_email_body=DEFAULT_INTERVIEW_EMAIL_BODY, rejection_email_subject=DEFAULT_REJECTION_EMAIL_SUBJECT, rejection_email_body=DEFAULT_REJECTION_EMAIL_BODY)
        attach_seed_file(career_page_settings, 'hero_image', 'static/img/seed/page-heroes/engineering_discussion_in_modern_factory.webp', 'careers-hero.webp')
        for order, (value, label, desc, icon) in enumerate([('3+', 'Active departments', 'Engineering, HSE & Quality, and Administration opportunities.', '▣'), ('100%', 'Online application', 'Applicants can submit CVs and documents directly from the job page.', '↗'), ('Email', 'Interview invite', 'Shortlisted applicants receive official invitation details by email.', '✉')], 1):
            up(CareerStat, {'label': label}, value=value, description=desc, icon_text=icon, show_on_hero=True, sort_order=order, is_active=True)
        for order, (title, desc, icon) in enumerate([('Project-ready environment', 'Work with teams focused on practical execution, coordination and dependable delivery.', '🏗'), ('Safety and quality focus', 'Build your career in a workplace that respects safe work practices and quality standards.', '✓'), ('Clear review workflow', 'Applications, documents and interview invitations are managed through a structured admin process.', '📄')], 1):
            up(CareerBenefit, {'title': title}, description=desc, icon_text=icon, sort_order=order, is_active=True)
        for order, (number, title, desc) in enumerate([('01', 'Apply Online', 'Submit your CV and supporting documents through the job page.'), ('02', 'Admin Review', 'HR reviews applicants inside the admin panel and checks documents.'), ('03', 'Interview Invite', 'Shortlisted applicants receive interview date, location and instructions by email.'), ('04', 'Selection', 'Final candidates are selected according to role requirements and project needs.')], 1):
            up(CareerProcessStep, {'step_number': number}, title=title, description=desc, sort_order=order, is_active=True)
        career_departments = [
            ('engineering', 'Engineering', 'Electrical, civil, mechanical and project engineering roles.'),
            ('hse-quality', 'HSE & Quality', 'Safety, quality and compliance-focused roles.'),
            ('administration', 'Administration', 'Office, HR, document control and support roles.'),
        ]
        department_map = {}
        for order, (slug, name, desc) in enumerate(career_departments, 1):
            department_map[slug] = up(CareerDepartment, {'slug': slug}, name=name, description=desc, sort_order=order, is_active=True)
        sample_jobs = [
            {
                "title": "Electrical Site Engineer",
                "code": "SES-ENG-001",
                "dept": "engineering",
                "location": "Dammam, Saudi Arabia",
                "emp_type": "full_time",
                "work_mode": "site",
                "job_level": "mid",
                "exp": "3+ years",
                "salary": "",
                "show_salary": False,
                "summary": "Lead site electrical work coordination, drawing review and daily execution support for industrial projects.",
                "description": "The Electrical Site Engineer supports daily execution, drawing coordination, material follow-up and site reporting for SESCCO project teams.\n\nThe role requires practical site coordination, discipline, safety awareness and clear communication with supervisors, QA/QC and client representatives.",
                "resp": "Coordinate daily site electrical activities.\nReview drawings, material requirements and work fronts.\nCoordinate with supervisors, QA/QC and client representatives.\nPrepare progress updates and support safe work execution.",
                "req": "Degree or diploma in Electrical Engineering.\nMinimum 3 years of site experience.\nStrong knowledge of drawings, materials and site coordination.\nGood communication and documentation skills.",
                "qual": "Electrical engineering degree or diploma.\nSaudi project site experience preferred.\nAbility to read drawings and technical documents.",
                "skills": "Site coordination.\nDrawing review.\nDaily reporting.\nSafety communication.",
                "benefits": "Competitive package according to experience.\nProfessional project environment.\nOpportunity to work on industrial and infrastructure projects.",
                "order": 1,
                "featured": True,
            },
            {
                "title": "HSE Officer",
                "code": "SES-HSE-002",
                "dept": "hse-quality",
                "location": "Eastern Province, Saudi Arabia",
                "emp_type": "full_time",
                "work_mode": "site",
                "job_level": "mid",
                "exp": "2+ years",
                "salary": "",
                "show_salary": False,
                "summary": "Support site safety implementation, inspections, toolbox talks and safety documentation.",
                "description": p("The HSE Officer supports safe work practices at project sites through inspections, toolbox talks, reporting and follow-up with the site team.", "This role is suitable for candidates who are organized, practical and committed to maintaining safety standards on active construction or industrial sites."),
                "resp": "Conduct site safety inspections and observations.\nSupport toolbox talks and safety briefings.\nMaintain safety records and support incident reporting.\nCoordinate with project teams to close safety actions.",
                "req": "Diploma or relevant safety qualification.\nNEBOSH / OSHA certificate preferred.\nExperience in construction or industrial project sites.\nGood reporting and communication skills.",
                "qual": "Relevant safety certificate preferred.\nKnowledge of site safety documentation.\nAbility to communicate with workers and supervisors.",
                "skills": "Inspection reporting.\nToolbox talk support.\nIncident documentation.\nCorrective action follow-up.",
                "benefits": "Safety-focused working culture.\nProject exposure across Saudi Arabia.\nGrowth opportunity within HSE function.",
                "order": 2,
                "featured": True,
            },
            {
                "title": "Document Controller",
                "code": "SES-ADM-003",
                "dept": "administration",
                "location": "Dammam Office",
                "emp_type": "full_time",
                "work_mode": "office",
                "job_level": "junior",
                "exp": "1+ years",
                "salary": "",
                "show_salary": False,
                "summary": "Manage project documents, submissions, registers and controlled records for the engineering team.",
                "description": p("The Document Controller maintains organized project documents, registers, submissions and revision tracking for office and project teams.", "The role requires accuracy, file discipline, Excel knowledge and professional follow-up with internal departments."),
                "resp": "Maintain incoming and outgoing document registers.\nControl revisions, submissions and approvals.\nCoordinate with project and admin teams.\nKeep digital and physical records organized.",
                "req": "Experience with document control or project administration.\nStrong Excel and file management skills.\nAttention to detail and professional communication.\nArabic and English communication preferred.",
                "qual": "Diploma or office administration background preferred.\nDocument control experience is an advantage.\nGood computer and filing skills.",
                "skills": "Excel registers.\nFile naming and archiving.\nEmail coordination.\nSubmission tracking.",
                "benefits": "Office-based role.\nStructured document workflow.\nLong-term growth in project administration.",
                "order": 3,
                "featured": False,
            },
        ]
        for job in sample_jobs:
            up(
                JobOpening,
                {'slug': slugify(job['title'])},
                title=job['title'],
                job_code=job['code'],
                department=department_map[job['dept']],
                location=job['location'],
                employment_type=job['emp_type'],
                work_mode=job['work_mode'],
                job_level=job['job_level'],
                experience_level=job['exp'],
                positions_available=1,
                summary=job['summary'],
                job_description=job['description'],
                responsibilities=job['resp'],
                requirements=job['req'],
                qualifications=job['qual'],
                skills=job['skills'],
                benefits=job['benefits'],
                salary_range=job['salary'],
                show_salary=job['show_salary'],
                apply_button_text='Apply Now',
                status='published',
                is_featured=job['featured'],
                sort_order=job['order'],
                is_active=True,
                seo_title=f"{job['title']} | SESCCO Careers",
                seo_description=job['summary'][:250],
            )

        contact_page_settings = up(
            ContactPageSettings,
            {'id': 1},
            eyebrow='Contact Us',
            hero_title='Contact SESCCO with confidence.',
            hero_subtitle='Send your requirement to the right SESCCO team through one clean contact page.',
            intro_title='Start your project inquiry clearly.',
            intro_text='Share your requirement by email through the form. Our team will review it and respond from the official SESCCO email address.',
            notification_email='info@sescco.com',
            email_from_name='SESCCO Website',
            map_eyebrow='Find Us',
            map_title='Office location details are available on request.',
            map_subtitle='Exact map details are temporarily hidden while public contact information is being finalized.',
            google_map_embed_url='',
            google_map_url='',
            map_button_text='Open in Google Maps',
            show_contact_methods=True,
            show_offices=True,
            show_business_hours=True,
            show_map=False,
            show_faqs=True,
            show_whatsapp_cta=False,
        )
        attach_seed_file(contact_page_settings, 'hero_image', 'static/img/seed/page-heroes/industrial_site_inspection_under_clear_sky.webp', 'contact-hero.webp')
        for order,(title,value,icon,url,active) in enumerate([('Call Us','','☎','',False),('WhatsApp','','✣','',False),('Email Us','info@sescco.com','✉','mailto:info@sescco.com',True)],1): up(ContactMethod, {'title':title}, value=value, icon_text=icon, url=url, sort_order=order, is_active=active, show_on_contact_page=active, show_in_footer=active)
        up(
            OfficeLocation,
            {'name': 'Main Office'},
            address='Dammam, Eastern Province, Kingdom of Saudi Arabia',
            city='Dammam',
            country='Saudi Arabia',
            phone='',
            email='info@sescco.com',
            map_embed_url='',
            map_url='',
            is_primary=True,
            sort_order=1,
            is_active=True,
        )
        BusinessHour.objects.filter(day_label__in=['Sunday - Thursday', 'Friday - Saturday']).update(is_active=False)
        for order,(day,hours) in enumerate([('Saturday - Thursday','8:00 AM - 5:00 PM'),('Friday','Closed')],1): up(BusinessHour, {'day_label':day}, hours=hours, sort_order=order, is_active=True)
        for order,title in enumerate(['General Inquiry','Project Quotation','Document Request','Contract Support','Partnership','Career / HR Inquiry'],1):
            email_to = 'hr@sescco.com' if title == 'Career / HR Inquiry' else 'info@sescco.com'
            up(InquirySubject, {'title':title}, email_to=email_to, sort_order=order, is_active=True)
        for order,(q,a) in enumerate([('What services does SESCCO provide?','SESCCO provides electrical engineering, civil and architectural fit-out works, telecommunication services, contract support, electromechanical works and mechanical/fire-fighting services.'),('Do you offer services outside Dammam?','Yes. SESCCO supports projects across Saudi Arabia according to project requirements.'),('How quickly will I receive a response?','Our team aims to respond promptly after receiving your inquiry.'),('Can SESCCO provide personnel and equipment support?','Yes. Our contract support service provides qualified personnel and equipment support according to project needs.')],1): up(FAQ, {'question':q}, answer=p(a), sort_order=order, is_active=True)

        RobotsSettings.objects.update_or_create(id=1, defaults={'content':'User-agent: *\nAllow: /\nSitemap: /sitemap.xml\nSitemap: /localized-sitemap.xml'})
        SchemaMarkup.objects.update_or_create(title='SESCCO Organization', page_path='', defaults={'json_ld':'{"@context":"https://schema.org","@type":"Organization","name":"Summit Engineering Solutions Cont. Co.","alternateName":"SESCCO","url":"https://sescco.com","email":"info@sescco.com"}', 'is_active':True})
        self.stdout.write(self.style.SUCCESS('SESCCO production English CMS content seeded successfully.'))


        # Default official SESCCO logo. It is copied to media only when company.logo is empty,
        # so future admin logo changes are never overwritten.
        default_logo = Path(settings.BASE_DIR) / "static" / "img" / "brand" / "sescco-logo.svg"
        if company and not company.logo and default_logo.exists():
            with default_logo.open("rb") as logo_file:
                company.logo.save("sescco-logo.svg", File(logo_file), save=True)


        # ---------------------------------------------------------------------
        # Prototype-aligned production override: remove generic/demo homepage cards
        # and enforce SESCCO-specific visible highlights after all earlier seed logic.
        # ---------------------------------------------------------------------
        demo_titles = [
            "Integrated", "CMS", "CRUD", "Admin Editable", "Project Ready",
            "Multi-Discipline", "Structured company profile CMS ready for many companies."
        ]
        HomeHighlight.objects.filter(title__in=demo_titles).delete()
        HomeHighlight.objects.filter(value__in=["CMS", "CRUD", "Admin Editable", "Project Ready", "Multi-Discipline"]).delete()
        HomeHighlight.objects.filter(description__icontains="CMS ready for many companies").delete()
        HomeHighlight.objects.filter(description__icontains="managed from admin").delete()
        HomeHighlight.objects.filter(description__icontains="CRUD").delete()

        production_highlights = [
            ("Integrated Engineering", "Multi-Discipline Capability", "Electrical, civil, architectural, fit-out and contract support services delivered by one dependable team.", "□", 1),
            ("Project Execution Support", "Qualified Workforce", "Skilled project teams, equipment support and practical execution for demanding industrial and infrastructure projects.", "⚙", 2),
            ("Safety & Quality Focus", "Reliable Delivery", "Work guided by safety, quality, efficiency and long-term client trust across Saudi Arabia.", "✓", 3),
        ]
        for title, value, description, icon, order in production_highlights:
            HomeHighlight.objects.update_or_create(title=title, defaults={
                "value": value,
                "description": description,
                "icon_text": icon,
                "link_text": "Learn More",
                "link_url": "/about/",
                "sort_order": order,
                "is_active": True,
            })


        # ---------------------------------------------------------------------
        # Upgrade 123: production data completeness pass.
        # This fills CMS-driven sections that templates can display as empty
        # admin previews when staff are logged in. Public visitors get complete
        # content while admins still retain full editing control.
        # ---------------------------------------------------------------------
        completeness_sections = [
            (home, "services_grid", "Integrated Capabilities", "One company for electrical, civil, fit-out, mechanical and contract support needs.", "<p>SESCCO brings practical engineering capability, site-ready teams and vendor-registered credibility together for industrial, utility and commercial projects.</p>", "Explore Services", "/services/", 1),
            (home, "projects_grid", "Experience Across Saudi Arabia", "Project references built through dependable execution.", "<p>From substation interface works and cable termination to civil construction, pipeline support and fit-out delivery, SESCCO’s portfolio reflects real field experience.</p>", "View Projects", "/projects/", 2),
            (about, "text_image", "What Makes SESCCO Reliable", "Structured delivery, qualified teams and clear communication.", "<p>Our work is guided by safety, quality, respect for people and long-term client relationships. We support each project with planning, resource coordination and practical execution discipline.</p>", "Contact SESCCO", "/contact/", 1),
        ]
        for page_obj, section_type, title, subtitle, content, button_text, button_url, order in completeness_sections:
            up(
                PageSection,
                {"page": page_obj, "section_type": section_type, "title": title},
                subtitle=subtitle,
                content=content,
                button_text=button_text,
                button_url=button_url,
                background_style="white",
                layout_style="standard",
                sort_order=order,
                is_active=True,
            )

        about_faqs = [
            ("What is SESCCO’s core business?", "SESCCO provides electrical engineering services, civil and architectural fit-out works, electromechanical works, mechanical and fire-fighting support, and contract support services."),
            ("Is SESCCO registered with major Saudi clients?", "Yes. SESCCO lists Saudi Aramco Vendor Code 10114560 and Saudi Electricity Company Vendor Code 02013075 in the company profile."),
            ("Where is SESCCO based?", "SESCCO is based in Dammam, Eastern Province, Kingdom of Saudi Arabia, and supports projects across the Kingdom according to project requirements."),
            ("What makes SESCCO a dependable partner?", "The company focuses on safety, quality, skilled workforce support, dependable service, and long-term client relationships built on trust and respect."),
        ]
        for order, (question, answer) in enumerate(about_faqs, 1):
            up(FAQ, {"page": about, "question": question}, answer=p(answer), sort_order=order, is_active=True)

        generic_pages = [
            ("quality-safety", "Quality & Safety", "Quality and Safety Commitment", "Execution guided by safety, quality and responsible project control.", "<p>SESCCO prioritizes safe work practices, quality-focused execution and respect for people and the environment. These principles support every service area and project activity.</p>"),
            ("vendor-registration", "Vendor Registration", "Vendor Registration Information", "Key vendor credentials for project and procurement review.", "<p>SESCCO’s company profile lists Saudi Aramco Vendor Code <strong>10114560</strong> and Saudi Electricity Company Vendor Code <strong>02013075</strong>.</p>"),
            ("capabilities", "Capabilities", "Engineering & Contracting Capabilities", "A clear overview of SESCCO’s service capabilities.", "<p>Core capabilities include electrical engineering services, civil and architectural fit-out works, contract support services, HVAC systems, fire detection and alarm systems, plumbing and sanitary works, fire suppression systems, and building lighting and power systems.</p>"),
        ]
        for slug, title, hero_title, hero_subtitle, body in generic_pages:
            page_obj = up(
                Page,
                {"slug": slug},
                title=title,
                template_type="generic",
                hero_title=hero_title,
                hero_subtitle=hero_subtitle,
                body=body,
                seo_title=f"{title} | SESCCO",
                seo_description=hero_subtitle,
                is_published=True,
            )
            up(GenericPageSettings, {"page": page_obj}, show_breadcrumbs=False, show_cta=True, content_width="standard", sidebar_enabled=False)
            up(PageSection, {"page": page_obj, "section_type": "cta", "title": "Need more information?"}, subtitle="Our team can share the right document or service details for your requirement.", content="<p>Contact SESCCO with your project, document or qualification request and the team will respond with the appropriate information.</p>", button_text="Contact Us", button_url="/contact/", sort_order=1, is_active=True)
            up(FAQ, {"page": page_obj, "question": "Can this information be updated from admin?"}, answer=p("Yes. This page and its custom CMS sections can be edited from the Django admin panel."), sort_order=1, is_active=True)

        source_depth_project_titles = {
            "Dismantling and Transportation of TFC at Haradh",
            "Preparation and Painting of 230kV OHTL Foundation",
            "The Avenues Khobar Plaster Works",
            "The Avenues Khobar Screed Works",
            "Mansura Massrah Gold Project Civil Works",
            "Novartis Office MEP and Architectural Fitout",
        }
        for project in Project.objects.filter(is_active=True):
            # Source-specific projects seeded below receive their own detailed scope
            # rows. Do not add generic rows to those projects on repeated seeding,
            # otherwise admin audit reports duplicate sort orders.
            if project.title in source_depth_project_titles:
                continue
            scope_seed = [
                ("Scope review", "Review project requirements, location, drawings and execution constraints before mobilization.", "01"),
                ("Site execution", "Coordinate project teams, materials and quality checks during the work phase.", "02"),
                ("Handover support", "Support completion records, close-out information and follow-up coordination where required.", "03"),
            ]
            for order, (title, description, icon) in enumerate(scope_seed, 1):
                up(ProjectScopeItem, {"project": project, "title": title}, description=description, icon_text=icon, sort_order=order, is_active=True)

        # Keep the admin section-order editor aligned with seeded public content.
        # Project detail sections are written as a complete canonical set so repeated
        # seeding cannot leave old/stale order values that move documents or related
        # projects above the case-study content.
        canonical_section_orders = [
            ("home", "custom_sections", "Custom SESCCO highlights", 100),
            ("about", "custom_sections", "Custom company sections", 90),
            ("about", "faqs", "About FAQs", 100),
            ("generic", "custom_sections", "Custom page sections", 30),
            ("generic", "faqs", "Generic page FAQs", 40),
            ("project_detail", "hero", "Project hero", 10),
            ("project_detail", "gallery", "Project gallery", 20),
            ("project_detail", "overview", "Project overview", 30),
            ("project_detail", "deliverables", "Key deliverables", 40),
            ("project_detail", "case_study", "Project case study", 50),
            ("project_detail", "detailed_scope", "Project detailed scope", 60),
            ("project_detail", "metrics", "Project quick metrics", 70),
            ("project_detail", "documents_cta", "Project documents and CTA", 80),
            ("project_detail", "related_projects", "Related projects", 90),
            ("clients_certifications", "hero", "Certifications and clients hero", 10),
            ("clients_certifications", "metrics", "Trust metrics", 15),
            ("clients_certifications", "clients", "Clients", 30),
            ("clients_certifications", "accreditations", "Accreditations", 40),
            ("clients_certifications", "standards", "Compliance standards", 50),
            ("clients_certifications", "testimonials", "Testimonials", 60),
            ("clients_certifications", "documents", "Documents", 70),
        ]
        PageSectionOrder.objects.filter(page_key="clients_certifications", section_key="partners").update(is_active=False)
        PageSectionOrder.objects.filter(page_key="clients_certifications", section_key="certificates").update(is_active=False)
        for page_key, section_key, label, order in canonical_section_orders:
            up(
                PageSectionOrder,
                {"page_key": page_key, "section_key": section_key},
                page_label=page_key.replace("_", " ").title(),
                section_label=label,
                description="Seeded production content is available; disable only if the section should be hidden.",
                sort_order=order,
                is_active=True,
            )
        cache.delete("cms_section_order_map")

        # ---------------------------------------------------------------------
        # Upgrade 124: company-profile project depth and service relationships.
        # Adds additional real project records from the English company profile,
        # replaces generic project detail blocks with source-specific scopes, and
        # links every seeded project to the matching service pages for stronger
        # related-project sections and production SEO.
        # ---------------------------------------------------------------------
        service_lookup = {svc.slug: svc for svc in Service.objects.filter(is_active=True)}
        electrical_service = service_lookup.get("electrical-engineering-services") or Service.objects.filter(title__icontains="Electrical").first()
        civil_service = service_lookup.get("civil-architectural-fitout-works") or Service.objects.filter(title__icontains="Civil").first()
        fitout_service = civil_service
        contract_service = service_lookup.get("contract-support-service") or Service.objects.filter(title__icontains="Contract").first()
        telecom_service = service_lookup.get("telecommunication-services") or Service.objects.filter(title__icontains="Telecommunication").first()
        mechanical_service = service_lookup.get("mechanical-fire-fighting-systems") or Service.objects.filter(title__icontains="Fire").first()

        profile_project_rows = [
            {
                "title": "Dismantling and Transportation of TFC at Haradh",
                "category": "Civil Projects",
                "client": "ARAMCO",
                "contractor": "TR",
                "location": "Haradh, Saudi Arabia",
                "status": "completed",
                "year": 2024,
                "duration": "Completed",
                "summary": "Dismantling and transportation of electrical equipment, plus demolition and dumping of TFC at Haradh.",
                "services": [civil_service, contract_service],
                "scopes": [
                    ("Dismantling works", "Dismantling of electrical equipment and related temporary facility components at Haradh.", "01"),
                    ("Transportation support", "Transportation coordination for removed equipment and project materials.", "02"),
                    ("Demolition and disposal", "Demolition and dumping of TFC elements according to project requirements.", "03"),
                ],
            },
            {
                "title": "Preparation and Painting of 230kV OHTL Foundation",
                "category": "Civil Projects",
                "client": "Future Technologies",
                "contractor": "SEPCO",
                "location": "Saudi Arabia",
                "status": "completed",
                "year": 2024,
                "duration": "Completed",
                "summary": "Supply of paint, preparation and painting of 230kV OHTL tower foundation as per SEC standard.",
                "services": [civil_service],
                "scopes": [
                    ("Surface preparation", "Preparation of 230kV OHTL tower foundation surfaces before coating.", "01"),
                    ("Paint supply", "Supply of approved paint materials according to project requirements.", "02"),
                    ("Foundation painting", "Painting works completed according to SEC standard requirements.", "03"),
                ],
            },
            {
                "title": "The Avenues Khobar Plaster Works",
                "category": "Architectural & Fitout Projects",
                "client": "The Avenues Khobar",
                "contractor": "Havelock1",
                "location": "Al Khobar, Saudi Arabia",
                "status": "ongoing",
                "year": 2025,
                "duration": "Starting November 2025",
                "summary": "Plaster work including mesh installation and angle installation for prayer rooms, bathrooms, corridors and other areas.",
                "services": [fitout_service],
                "scopes": [
                    ("Plaster works", "Plastering works for prayer rooms, bathrooms, corridors and related areas.", "01"),
                    ("Mesh installation", "Mesh installation support for prepared architectural surfaces.", "02"),
                    ("Angle installation", "Angle installation and finishing coordination for fit-out surfaces.", "03"),
                ],
            },
            {
                "title": "The Avenues Khobar Screed Works",
                "category": "Architectural & Fitout Projects",
                "client": "The Avenues Khobar",
                "contractor": "Havelock1",
                "location": "Al Khobar, Saudi Arabia",
                "status": "ongoing",
                "year": 2026,
                "duration": "Starting January 2026",
                "summary": "Screed work for prayer rooms, bathrooms, corridors and other areas at The Avenues Khobar.",
                "services": [fitout_service],
                "scopes": [
                    ("Screed works", "Screed application for prayer rooms, bathrooms, corridors and supporting areas.", "01"),
                    ("Area coordination", "Coordination of work fronts across multiple interior zones.", "02"),
                    ("Finishing support", "Support for durable and level surfaces ready for following fit-out activities.", "03"),
                ],
            },
            {
                "title": "Mansura Massrah Gold Project Civil Works",
                "category": "Civil Projects",
                "client": "Mansura Massrah Gold Project",
                "contractor": "L & T",
                "location": "Saudi Arabia",
                "status": "completed",
                "year": 2021,
                "duration": "22 Months (Feb 2021)",
                "summary": "Construction of substation building, infrastructure works, pipe rack, tunnel, water tank, conveyor belt, HFO and LFO circular works, UG/AG tanks, engine hall and warehouse.",
                "services": [civil_service, contract_service],
                "scopes": [
                    ("Substation building", "Civil construction support for substation building and related infrastructure.", "01"),
                    ("Industrial structures", "Pipe rack, tunnel, conveyor belt, engine hall and warehouse work packages.", "02"),
                    ("Tank and utility works", "Water tank, HFO/LFO circular works and UG/AG tank construction support.", "03"),
                ],
            },
            {
                "title": "Novartis Office MEP and Architectural Fitout",
                "category": "Architectural & Fitout Projects",
                "client": "Novartis",
                "contractor": "SESCCO Team",
                "location": "Al Khobar, Saudi Arabia",
                "status": "completed",
                "year": 2015,
                "duration": "Completed October 2015",
                "summary": "Complete MEP structure and architectural works covering approximately 1,300 sqm.",
                "services": [fitout_service, mechanical_service],
                "scopes": [
                    ("MEP structure", "MEP structure works for office fit-out requirements.", "01"),
                    ("Architectural covering", "Architectural covering and interior fit-out scope over approximately 1,300 sqm.", "02"),
                    ("Office delivery", "Coordinated fit-out delivery for a corporate office environment.", "03"),
                ],
            },
        ]

        for offset, row in enumerate(profile_project_rows, 40):
            category = pcats.get(row["category"]) or ProjectCategory.objects.filter(name=row["category"]).first()
            project = up(
                Project,
                {"slug": slugify(row["title"])},
                category=category,
                title=row["title"],
                client_name=row["client"],
                contractor_name=row["contractor"],
                location=row["location"],
                status=row["status"],
                year=row["year"],
                duration=row["duration"],
                short_description=row["summary"],
                summary=p(row["summary"]),
                challenge=p("The work required disciplined site coordination, safe execution and careful alignment with client requirements."),
                scope=p(row["summary"]),
                solution=p("SESCCO supported the project through practical supervision, skilled teams and controlled execution."),
                outcomes=p("The project strengthens SESCCO’s company-profile experience across industrial, utility and commercial environments."),
                sort_order=offset,
                is_featured=False,
                is_active=True,
                seo_title=f"{row['title']} | SESCCO Project Experience",
                seo_description=row["summary"][:250],
            )
            project.services.set([svc for svc in row["services"] if svc])
            media_config = project_media_map.get(project.slug)
            if media_config:
                hero_path, gallery_config = media_config
                gallery_paths = list(gallery_config) if isinstance(gallery_config, (list, tuple)) else []
                attach_project_gallery(project, hero_path, gallery_paths)
            else:
                clear_seeded_project_media(project)
            # Remove generic scope placeholders from earlier seeds so source-specific
            # scope rows remain the only active sort_order=1/2/3 items for these projects.
            ProjectScopeItem.objects.filter(project=project, title__in=["Scope review", "Site execution", "Handover support"]).delete()
            metric_values = [
                ("Location", row["location"]),
                ("Status", row["status"].title()),
                ("Duration", row["duration"]),
                ("Client", row["client"]),
                ("Contractor", row["contractor"]),
            ]
            for metric_order, (label, value) in enumerate(metric_values, 1):
                up(ProjectMetric, {"project": project, "label": label}, value=value, icon_text="•", sort_order=metric_order, is_active=True)
            for scope_order, (title, description, icon) in enumerate(row["scopes"], 1):
                up(ProjectScopeItem, {"project": project, "title": title}, description=description, icon_text=icon, sort_order=scope_order, is_active=True)
            project_cta = up(ProjectCTA, {"project": project}, title="Need a similar project partner?", subtitle="Contact SESCCO to discuss your engineering or contracting requirements.", button_text="Start a Project", button_url="/contact/", is_active=True)
            localize_project_cta(project_cta)

        service_project_links = {
            "Replacement of Existing Outdoor Aindar Sub-30 with New GIS Substation": [electrical_service],
            "Yanbu 4 - 110kV HV Substation Interface Works": [electrical_service],
            "Replacement of 13.8kV SWGR": [electrical_service],
            "MV Cable Fault Location Test, Damage Repair and Termination": [electrical_service],
            "EPCC 10,000TPD Clinker Cement Plant Civil Works": [civil_service],
            "EPCC 10,000TPD Clinker Cement Plant Architectural & Fitout Works": [fitout_service],
            "Roshan Ewan Sedra 2 Villas Tile Works": [fitout_service],
            "Haradh RTR Pipeline Project": [civil_service, contract_service],
            "Jafurah Upstream Pipeline Project": [civil_service, contract_service],
            "The Avenues Khobar Plaster and Screed Works": [fitout_service],
            "McDermott Arabia Office Fitout": [fitout_service],
            "Worley Parsons Office Fitout": [fitout_service],
            "Fire-Fighting System Installation for Industrial Facility and Warehouse": [mechanical_service],
            "Ethernet Cable Installation and Testing Works": [telecom_service, electrical_service],
            "Telecommunication Cabinet and Network Support Works": [telecom_service],
            "SEPCO Telecommunication Field Support Works": [telecom_service],
            "OPGW Fiber Splicing and Testing Works": [telecom_service],
            "Asphalting and Site Preparation Works": [civil_service],
        }
        for title, related_services in service_project_links.items():
            project = Project.objects.filter(title=title).first()
            if project:
                project.services.set([svc for svc in related_services if svc])

        # Bring list-page stats closer to the now-seeded project portfolio.
        stat_updates = [
            ("Profile Projects", f"{Project.objects.filter(is_active=True).count()}+"),
            ("Electrical Projects", "8+"),
            ("Civil Projects", "8+"),
            ("Fitout Projects", "8+"),
            ("Core Clients", "29+"),
        ]
        for order, (label, value) in enumerate(stat_updates, 1):
            up(ProjectListStat, {"label": label}, value=value, icon_text="▣", sort_order=order, is_active=True)


        # ---------------------------------------------------------------------
        # Upgrade 125: production document center, service brochures and SEO.
        # Makes the service-detail brochure card actionable, expands the
        # downloads center with capability documents, and adds page-level schema.
        # ---------------------------------------------------------------------
        shared_profile_media_path = "documents/files/sescco-company-profile-en.pdf"
        service_docs_category = up(
            DocumentCategory,
            {"slug": "service-capability-sheets"},
            name="Service Capability Sheets",
            icon_text="PDF",
            sort_order=2,
            is_active=True,
        )
        compliance_docs_category = up(
            DocumentCategory,
            {"slug": "vendor-compliance-documents"},
            name="Vendor & Compliance Documents",
            icon_text="DOC",
            sort_order=3,
            is_active=True,
        )

        capability_documents = [
            ("Electrical Engineering Capability Sheet", "Electrical engineering service profile covering GIS, transformers, panels, MV/LV cable works, lighting and power systems."),
            ("Civil and Fitout Capability Sheet", "Civil construction, architectural fit-out, plastering, painting, screed, tile and infrastructure capability reference."),
            ("Contract Support Capability Sheet", "Workforce, equipment and project support capability reference for resource planning and site execution."),
            ("Electromechanical Works Capability Sheet", "HVAC, fire detection and alarm, plumbing, sanitary, fire suppression, building lighting and power capability reference."),
            ("Mechanical and Fire-Fighting Capability Sheet", "Mechanical and fire-fighting system installation capability reference for industrial facilities and warehouses."),
        ]
        for order, (title, description) in enumerate(capability_documents, 10):
            doc = up(
                DownloadDocument,
                {"slug": slugify(title)},
                category=service_docs_category,
                title=title,
                description=description,
                file_type="PDF",
                version="2026.1",
                file_size="21 MB",
                is_featured=False,
                is_public=True,
                requires_request=False,
                access_level="public",
                preview_enabled=True,
                sort_order=order,
                is_active=True,
            )
            if not doc.file:
                doc.file.name = shared_profile_media_path
                doc.save(update_fields=["file", "file_size", "updated_at"])

        vendor_documents = [
            ("Saudi Aramco Vendor Code Reference", "SESCCO vendor reference: Saudi Aramco Vendor Code 10114560."),
            ("SEC Vendor Code Reference", "SESCCO vendor reference: Saudi Electricity Company Vendor Code 02013075."),
            ("Quality, Safety and Environmental Commitment", "SESCCO commitment reference covering quality management, environmental responsibility and occupational health & safety."),
        ]
        for order, (title, description) in enumerate(vendor_documents, 30):
            doc = up(
                DownloadDocument,
                {"slug": slugify(title)},
                category=compliance_docs_category,
                title=title,
                description=description,
                file_type="PDF",
                version="2026.1",
                file_size="21 MB",
                is_featured=False,
                is_public=True,
                requires_request=False,
                access_level="public",
                preview_enabled=True,
                sort_order=order,
                is_active=True,
            )
            if not doc.file:
                doc.file.name = shared_profile_media_path
                doc.save(update_fields=["file", "file_size", "updated_at"])

        # Reuse the seeded company profile PDF as the public brochure for every
        # service page. This removes the fallback Contact Us button from the
        # brochure card and gives visitors a real document immediately.
        for service in Service.objects.filter(is_active=True):
            if not service.brochure:
                service.brochure.name = shared_profile_media_path
                service.save(update_fields=["brochure", "updated_at"])

        service_item_list = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "SESCCO Services",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": service.title,
                    "url": f"https://sescco.com/services/{service.slug}/",
                    "description": service.short_description,
                }
                for index, service in enumerate(Service.objects.filter(is_active=True).order_by("sort_order", "id"), 1)
            ],
        }
        project_item_list = {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": "SESCCO Project Experience",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": project.title,
                    "url": f"https://sescco.com/projects/{project.slug}/",
                    "description": project.short_description,
                }
                for index, project in enumerate(Project.objects.filter(is_active=True).order_by("sort_order", "id")[:25], 1)
            ],
        }
        downloads_collection = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": "SESCCO Company Profile and Documents",
            "url": "https://sescco.com/downloads/",
            "description": "Company profile, capability sheets, vendor references and compliance documents for Summit Engineering Solutions Cont. Co.",
        }
        SchemaMarkup.objects.update_or_create(
            title="SESCCO Services ItemList",
            page_path="/services/",
            defaults={"json_ld": json.dumps(service_item_list, ensure_ascii=False), "is_active": True},
        )
        SchemaMarkup.objects.update_or_create(
            title="SESCCO Projects ItemList",
            page_path="/projects/",
            defaults={"json_ld": json.dumps(project_item_list, ensure_ascii=False), "is_active": True},
        )
        SchemaMarkup.objects.update_or_create(
            title="SESCCO Downloads Collection",
            page_path="/downloads/",
            defaults={"json_ld": json.dumps(downloads_collection, ensure_ascii=False), "is_active": True},
        )
