PAGE_SECTION_REGISTRY = {
    "home": {
        "label": "Home page",
        "sections": [
            ("hero", "Hero", "Main homepage hero title, image and buttons"),
            ("trust_strip", "Trust strip", "Vendor codes, established year, clients and certificate metrics"),
            ("highlights", "Capability highlights", "Homepage compact capability cards"),
            ("leadership", "Leadership message", "Managing committee / leadership message block"),
            ("about", "About preview", "Homepage about section content and image"),
            ("services", "Featured services", "Featured service cards"),
            ("projects", "Featured projects", "Featured project cards"),
            ("proof", "Clients and certificates preview", "Home clients and selected certificates preview"),
            ("why_choose", "Why choose cards", "Safety, quality, workforce and capability cards"),
            ("custom_sections", "Custom page sections", "Reusable admin-created custom sections"),
        ],
    },
    "about": {
        "label": "About page",
        "sections": [
            ("hero", "Hero", "About hero title, subtitle and image"),
            ("trust_strip", "Trust strip", "Company trust metrics"),
            ("overview", "Company overview", "Overview image and body copy"),
            ("mission_vision", "Mission, vision and values", "Purpose, mission, vision and values cards"),
            ("timeline", "Journey timeline", "Milestones and achievement timeline"),
            ("strengths", "Strengths", "About strengths / why choose cards"),
            ("stats", "Stats", "About statistic cards"),
            ("leadership", "Leadership message", "Bottom managing committee message"),
            ("custom_sections", "Custom sections", "Reusable admin-created custom sections"),
            ("faqs", "FAQs", "About page questions"),
        ],
    },
    "services_list": {
        "label": "Services list page",
        "sections": [
            ("hero", "Hero", "Services page hero with optional parallax background"),
            ("search_services", "Search and services grid", "Realtime search, categories, sorting and all service cards"),
            ("featured_service", "Featured service", "Highlighted featured service CTA"),
            ("process", "Service process", "Service list process steps"),
            ("faqs", "Service questions", "Services page FAQs"),
        ],
    },
    "service_detail": {
        "label": "Service detail page",
        "sections": [
            ("hero", "Hero", "Service hero, cover image, CTA buttons"),
            ("key_points", "Key points", "Top service key points"),
            ("related_projects", "Related projects", "Projects connected to this service"),
            ("body_summary", "Body and summary", "Main service body and summary card"),
            ("deliverables", "Deliverables", "Service deliverables"),
            ("features", "Features", "Service feature cards"),
            ("process", "Process", "Service process steps"),
            ("brochure", "Brochure CTA", "Download/contact service CTA"),
            ("faqs", "FAQs", "Service detail FAQs"),
        ],
    },
    "projects_list": {
        "label": "Projects list page",
        "sections": [
            ("hero", "Hero", "Projects page hero"),
            ("stats", "Project stats", "Portfolio stats"),
            ("portfolio", "Portfolio grid", "Intro, filters, featured project and project cards"),
            ("client_strip", "Client strip", "Clients served in projects"),
            ("cta", "CTA", "Project list call to action"),
        ],
    },
    "project_detail": {
        "label": "Project detail page",
        "sections": [
            ("hero", "Hero", "Project title, cover and quick hero facts"),
            ("gallery", "Slideshow gallery", "Project image slideshow"),
            ("overview", "Overview and glance", "Project description and at-a-glance facts"),
            ("deliverables", "Key deliverables", "Project deliverables strip"),
            ("case_study", "Case study blocks", "Challenge, scope, solution and outcome cards"),
            ("detailed_scope", "Detailed scope", "Numbered detailed scope / execution step cards"),
            ("metrics", "Metrics", "Project performance metrics"),
            ("documents_cta", "Documents and CTA", "Project files and enquiry CTA"),
            ("related_projects", "Related projects", "Related project rail"),
        ],
    },
    "clients_certifications": {
        "label": "Certifications & clients page",
        "sections": [
            ("hero", "Hero", "Certifications and clients hero"),
            ("metrics", "Trust metrics", "Vendor codes and trust metrics"),
            ("certificates", "Certificates", "Certificate image grid and modal"),
            ("clients", "Clients", "Client logo grid and filters"),
            ("accreditations", "Accreditations", "Accreditation references"),
            ("standards", "Compliance standards", "Compliance and standards cards"),
            ("testimonials", "Testimonials", "Client testimonials"),
            ("documents", "Documents", "Supporting documents"),
        ],
    },
    "careers": {
        "label": "Careers page",
        "sections": [
            ("hero", "Hero", "Career page hero and action buttons"),
            ("stats", "Career stats", "Stats shown near hero"),
            ("jobs", "Open roles", "Job search, filters and listings"),
            ("benefits", "Benefits", "Why work with us cards"),
            ("process", "Hiring process", "Career process steps"),
            ("cta", "Career CTA", "HR contact CTA"),
        ],
    },
    "contact": {
        "label": "Contact page",
        "sections": [
            ("hero", "Hero", "Contact hero with optional parallax background"),
            ("intro_form", "Intro and contact form", "Contact intro text and inquiry form"),
            ("map", "Google map", "Admin-editable Google map embed and directions URL"),
            ("offices", "Office locations", "Additional office locations when more than one office exists"),
            ("faqs", "FAQs", "Contact page FAQs"),
        ],
    },
    "generic": {
        "label": "Generic CMS pages",
        "sections": [
            ("hero", "Hero", "Generic page hero"),
            ("body", "Main body", "Generic page CKEditor body and optional sidebar"),
            ("custom_sections", "Custom sections", "Dynamic custom page sections"),
            ("faqs", "FAQs", "Generic page FAQs"),
        ],
    },
}


def iter_default_sections():
    for page_key, page_data in PAGE_SECTION_REGISTRY.items():
        for index, (section_key, label, description) in enumerate(page_data["sections"], start=1):
            yield {
                "page_key": page_key,
                "page_label": page_data["label"],
                "section_key": section_key,
                "section_label": label,
                "description": description,
                "sort_order": index,
            }
