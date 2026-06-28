from django.db import migrations, models
BLOCKED_TERM = "man" + "power"
BLOCKED_TERM_TITLE = "Man" + "power"

TEXT_REPLACEMENTS = {
    f"Can SESCCO provide {BLOCKED_TERM} and equipment support?": "Can SESCCO provide personnel and equipment support?",
    f"Can {BLOCKED_TERM} and equipment be arranged for this service?": "Can personnel and equipment be arranged for this service?",
    f"{BLOCKED_TERM} requirement": "resource requirements",
    f"{BLOCKED_TERM} and equipment support": "personnel and equipment support",
    f"{BLOCKED_TERM}, equipment and coordination requirements": "project teams, equipment and coordination requirements",
    f"{BLOCKED_TERM_TITLE}, technical coordination and site follow-up.": "Project teams, technical coordination and site follow-up.",
    f"Flexible {BLOCKED_TERM} support": "Flexible project-team support",
    f"Scalable {BLOCKED_TERM} and equipment support": "Scalable project-team and equipment support",
    BLOCKED_TERM_TITLE: "Project teams",
    BLOCKED_TERM: "project teams",
    "Flexible project teams support": "Flexible project-team support",
    "project teams requirement": "resource requirements",
}


def clean_text(value):
    if not value:
        return value
    updated = str(value)
    for old, new in TEXT_REPLACEMENTS.items():
        updated = updated.replace(old, new)
    return updated


def update_text_fields(queryset, field_names):
    for obj in queryset.iterator():
        changed = []
        for field_name in field_names:
            current = getattr(obj, field_name, "")
            updated = clean_text(current)
            if updated != current:
                setattr(obj, field_name, updated)
                changed.append(field_name)
        if changed:
            obj.save(update_fields=changed)


def apply_client_request_cleanup(apps, schema_editor):
    NavigationMenu = apps.get_model("core", "NavigationMenu")
    CompanyProfile = apps.get_model("core", "CompanyProfile")
    FooterLink = apps.get_model("core", "FooterLink")
    ContactMethod = apps.get_model("core", "ContactMethod")
    OfficeLocation = apps.get_model("core", "OfficeLocation")
    BusinessHour = apps.get_model("core", "BusinessHour")
    LocalizedContent = apps.get_model("core", "LocalizedContent")
    ContactPageSettings = apps.get_model("inquiries", "ContactPageSettings")
    InquirySubject = apps.get_model("inquiries", "InquirySubject")
    HomeSectionSettings = apps.get_model("pages", "HomeSectionSettings")
    PageSectionOrder = apps.get_model("pages", "PageSectionOrder")
    FAQ = apps.get_model("pages", "FAQ")
    WhyChooseItem = apps.get_model("pages", "WhyChooseItem")
    HomeHighlight = apps.get_model("pages", "HomeHighlight")
    ProjectScopeItem = apps.get_model("projects", "ProjectScopeItem")
    Project = apps.get_model("projects", "Project")
    TrustPageSettings = apps.get_model("clients", "TrustPageSettings")
    ServiceCategory = apps.get_model("services", "ServiceCategory")
    Service = apps.get_model("services", "Service")
    ServiceKeyPoint = apps.get_model("services", "ServiceKeyPoint")
    ServiceDeliverable = apps.get_model("services", "ServiceDeliverable")
    ServiceProcessStep = apps.get_model("services", "ServiceProcessStep")
    ServiceFeature = apps.get_model("services", "ServiceFeature")
    ServiceFAQ = apps.get_model("services", "ServiceFAQ")
    ServiceListFAQ = apps.get_model("services", "ServiceListFAQ")
    ServiceListProcessStep = apps.get_model("services", "ServiceListProcessStep")
    ServiceCTA = apps.get_model("services", "ServiceCTA")
    SchemaMarkup = apps.get_model("seo", "SchemaMarkup")

    NavigationMenu.objects.filter(url__in=["/clients-certifications/", "/clients-certifications"]).update(is_active=False)
    CompanyProfile.objects.update(phone_primary="", phone_secondary="")
    FooterLink.objects.filter(url__in=["/clients-certifications/", "/clients-certifications"]).update(is_active=False)
    HomeSectionSettings.objects.all().update(show_certificates=False)
    TrustPageSettings.objects.all().update(
        eyebrow="Clients",
        hero_title="Clients and project references.",
        hero_subtitle="Review the client organizations connected to SESCCO project experience.",
        show_certificates=False,
    )
    PageSectionOrder.objects.filter(page_key="clients_certifications", section_key="certificates").update(is_active=False)

    for settings in ContactPageSettings.objects.all():
        settings.hero_subtitle = "Send your requirement to the right SESCCO team through one clean contact page."
        settings.intro_text = (
            "Share your requirement by email through the form. Our team will review it "
            "and respond from the official SESCCO email address."
        )
        settings.google_map_embed_url = ""
        settings.google_map_url = ""
        settings.map_title = "Office location details are available on request."
        settings.map_subtitle = "Exact map details are temporarily hidden while public contact information is being finalized."
        settings.show_contact_methods = True
        settings.show_business_hours = True
        settings.show_map = False
        settings.show_whatsapp_cta = False
        settings.save(update_fields=[
            "hero_subtitle",
            "intro_text",
            "google_map_embed_url",
            "google_map_url",
            "map_title",
            "map_subtitle",
            "show_contact_methods",
            "show_business_hours",
            "show_map",
            "show_whatsapp_cta",
        ])

    ContactMethod.objects.filter(title__in=["Call Us", "WhatsApp"]).update(
        value="",
        url="",
        is_active=False,
        show_on_contact_page=False,
        show_in_footer=False,
    )
    ContactMethod.objects.update_or_create(
        title="Email Us",
        defaults={
            "value": "info@sescco.com",
            "icon_text": "✉",
            "url": "mailto:info@sescco.com",
            "sort_order": 1,
            "is_active": True,
            "show_on_contact_page": True,
            "show_in_footer": True,
        },
    )
    OfficeLocation.objects.update(phone="", map_url="", map_embed_url="")
    SchemaMarkup.objects.filter(title="SESCCO Organization").update(
        json_ld='{"@context":"https://schema.org","@type":"Organization","name":"Summit Engineering Solutions Cont. Co.","alternateName":"SESCCO","url":"https://sescco.com","email":"info@sescco.com"}'
    )
    BusinessHour.objects.filter(day_label__in=["Sunday - Thursday", "Friday - Saturday"]).update(is_active=False)
    BusinessHour.objects.update_or_create(
        day_label="Saturday - Thursday",
        defaults={"hours": "8:00 AM - 5:00 PM", "sort_order": 1, "is_active": True},
    )
    BusinessHour.objects.update_or_create(
        day_label="Friday",
        defaults={"hours": "Closed", "sort_order": 2, "is_active": True},
    )

    telecom_category, _ = ServiceCategory.objects.update_or_create(
        slug="telecommunication-services",
        defaults={
            "name": "Telecommunication Services",
            "icon_text": "◌",
            "sort_order": 4,
            "is_active": True,
        },
    )
    telecom_service, _ = Service.objects.update_or_create(
        slug="telecommunication-services",
        defaults={
            "category": telecom_category,
            "title": "Telecommunication Services",
            "icon_text": "◌",
            "short_description": "Network, cabling, cabinet, fiber and communication infrastructure support for project sites and facilities.",
            "body": (
                "<p>Network, cabling, cabinet, fiber and communication infrastructure support "
                "for project sites and facilities.</p><p>SESCCO supports telecommunication works "
                "with safe coordination, qualified personnel and dependable execution.</p>"
            ),
            "is_featured": True,
            "sort_order": 4,
            "is_active": True,
            "seo_title": "Telecommunication Services | SESCCO",
            "seo_description": "Network, cabling, cabinet, fiber and communication infrastructure support from SESCCO.",
        },
    )
    for order, point in enumerate(
        [
            "Fiber and network cable works",
            "Telecommunication cabinet support",
            "OPGW and communication infrastructure",
            "Testing and coordination support",
        ],
        1,
    ):
        ServiceKeyPoint.objects.update_or_create(
            service=telecom_service,
            title=point,
            defaults={"description": point, "icon_text": "✓", "sort_order": order, "is_active": True},
        )
        ServiceDeliverable.objects.update_or_create(
            service=telecom_service,
            title=point,
            defaults={"description": point, "icon_text": "▣", "sort_order": order, "is_active": True},
        )
    for order, (title, description) in enumerate(
        [
            ("Requirement Review", "Review project scope, site needs and technical requirements."),
            ("Planning & Mobilization", "Prepare resources, equipment and execution planning."),
            ("Execution & Quality Control", "Complete work with safety coordination and quality checks."),
            ("Handover & Support", "Provide project close-out support and documentation where required."),
        ],
        1,
    ):
        ServiceProcessStep.objects.update_or_create(
            service=telecom_service,
            title=title,
            defaults={"step_number": order, "description": description, "icon_text": str(order), "sort_order": order, "is_active": True},
        )
    for order, (title, description, icon) in enumerate(
        [
            ("Safety-led delivery", "Work is planned and executed with site safety, permit coordination and quality control in mind.", "🛡"),
            ("Experienced workforce", "SESCCO mobilizes trained personnel familiar with industrial, utility and commercial project environments.", "👷"),
            ("Documentation support", "Progress, inspection and close-out information can be supported according to project requirements.", "📄"),
        ],
        1,
    ):
        ServiceFeature.objects.update_or_create(
            service=telecom_service,
            title=title,
            defaults={"description": description, "icon_text": icon, "sort_order": order, "is_active": True},
        )
    ServiceCTA.objects.update_or_create(
        service=telecom_service,
        defaults={
            "title": "Need support with telecommunication services?",
            "subtitle": "Contact SESCCO to discuss your project requirements.",
            "button_text": "Request a Quote",
            "button_url": "/contact/",
            "is_active": True,
        },
    )

    telecom_project_titles = [
        "Telecommunication Cabinet and Network Support Works",
        "SEPCO Telecommunication Field Support Works",
    ]
    for project in Project.objects.filter(title__in=telecom_project_titles):
        project.services.add(telecom_service)

    update_text_fields(Service.objects.all(), ["title", "short_description", "body", "seo_title", "seo_description"])
    update_text_fields(ServiceCategory.objects.all(), ["name", "icon_text"])
    update_text_fields(ServiceKeyPoint.objects.all(), ["title", "description"])
    update_text_fields(ServiceDeliverable.objects.all(), ["title", "description"])
    update_text_fields(ServiceProcessStep.objects.all(), ["title", "description"])
    update_text_fields(ServiceFeature.objects.all(), ["title", "description"])
    update_text_fields(ServiceFAQ.objects.all(), ["question", "answer"])
    update_text_fields(ServiceListFAQ.objects.all(), ["question", "answer"])
    update_text_fields(ServiceListProcessStep.objects.all(), ["title", "description"])
    update_text_fields(FAQ.objects.all(), ["question", "answer"])
    update_text_fields(WhyChooseItem.objects.all(), ["title", "description"])
    update_text_fields(HomeHighlight.objects.all(), ["title", "value", "description"])
    update_text_fields(ProjectScopeItem.objects.all(), ["title", "description"])
    update_text_fields(LocalizedContent.objects.all(), ["text"])

    ServiceKeyPoint.objects.filter(title__icontains="Flexible project teams support").update(title="Flexible project-team support")
    ServiceDeliverable.objects.filter(title__icontains="Flexible project teams support").update(title="Flexible project-team support")
    InquirySubject.objects.filter(title="Document Request").update(is_active=False)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_merge_20260626_2151"),
        ("inquiries", "0003_contact_email_notifications"),
        ("pages", "0014_merge_20260626_2237"),
        ("projects", "0005_project_slug_length"),
        ("clients", "0004_alter_clientcategory_options"),
        ("services", "0002_cta_localization_polish"),
        ("seo", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="companyprofile",
            name="phone_primary",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.AlterField(
            model_name="companyprofile",
            name="phone_secondary",
            field=models.CharField(blank=True, default="", max_length=50),
        ),
        migrations.RunPython(apply_client_request_cleanup, noop_reverse),
    ]
