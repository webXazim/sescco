from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class TranslationTarget:
    model_label: str
    content_type: str
    fields: tuple[str, ...]


TRANSLATION_TARGETS = [
    TranslationTarget("Static UI Text", "statictext", ("text",)),
    TranslationTarget("Company Profile", "companyprofile", ("company_name", "short_name", "tagline", "description")),
    TranslationTarget("Navigation", "navigationmenu", ("title",)),
    TranslationTarget("Footer Column", "footercolumn", ("title",)),
    TranslationTarget("Footer Link", "footerlink", ("title",)),
    TranslationTarget("CTA Settings", "ctasettings", ("header_cta_text", "main_cta_title", "main_cta_subtitle", "main_cta_button_text")),
    TranslationTarget("CTA Section", "ctasection", ("title", "subtitle", "button_text")),
    TranslationTarget("Home Hero", "homehero", ("title", "subtitle", "primary_button_text", "secondary_button_text")),
    TranslationTarget("Home About", "homeaboutblock", ("eyebrow", "title", "body", "button_text")),
    TranslationTarget("Home Settings", "homesectionsettings", ("services_eyebrow", "services_title", "projects_eyebrow", "projects_title", "clients_eyebrow", "certificates_eyebrow", "why_choose_eyebrow", "why_choose_title")),
    TranslationTarget("Home Highlight", "homehighlight", ("title", "value", "description", "link_text")),
    TranslationTarget("Why Choose Item", "whychooseitem", ("title", "description")),
    TranslationTarget("Page", "page", ("title", "hero_title", "hero_subtitle", "body", "seo_title", "seo_description")),
    TranslationTarget("Page Section", "pagesection", ("title", "subtitle", "content", "button_text")),
    TranslationTarget("Mission/Vision", "missionvisionitem", ("title", "description")),
    TranslationTarget("Value Item", "valueitem", ("title", "description")),
    TranslationTarget("Timeline Item", "timelineitem", ("title", "description")),
    TranslationTarget("Leadership Message", "leadershipmessage", ("title", "message", "person_designation")),
    TranslationTarget("Stats", "statitem", ("label", "value")),
    TranslationTarget("FAQ", "faq", ("question", "answer")),
    TranslationTarget("Service Page Settings", "servicelistpagesettings", ("eyebrow", "hero_title", "hero_subtitle", "intro_title", "intro_text")),
    TranslationTarget("Service", "service", ("title", "short_description", "body", "seo_title", "seo_description")),
    TranslationTarget("Service Key Point", "servicekeypoint", ("title", "description")),
    TranslationTarget("Service Deliverable", "servicedeliverable", ("title", "description")),
    TranslationTarget("Service Feature", "servicefeature", ("title", "description")),
    TranslationTarget("Service Process", "serviceprocessstep", ("title", "description")),
    TranslationTarget("Service FAQ", "servicefaq", ("question", "answer")),
    TranslationTarget("Service CTA", "servicecta", ("title", "subtitle", "button_text")),
    TranslationTarget("Project Page Settings", "projectlistpagesettings", ("eyebrow", "hero_title", "hero_subtitle", "intro_title", "intro_text")),
    TranslationTarget("Project", "project", ("title", "short_description", "summary", "challenge", "scope", "solution", "outcomes", "seo_title", "seo_description")),
    TranslationTarget("Project Stat", "projectliststat", ("label", "value")),
    TranslationTarget("Project Metric", "projectmetric", ("label", "value")),
    TranslationTarget("Project Scope Item", "projectscopeitem", ("title", "description")),
    TranslationTarget("Project CTA", "projectcta", ("title", "subtitle", "button_text")),
    TranslationTarget("Trust Page Settings", "trustpagesettings", ("eyebrow", "hero_title", "hero_subtitle", "clients_eyebrow", "clients_title", "partners_eyebrow", "partners_title", "certificates_eyebrow", "certificates_title", "standards_eyebrow", "standards_title", "testimonials_eyebrow", "testimonials_title")),
    TranslationTarget("Client", "client", ("name", "category", "description")),
    TranslationTarget("Partner", "partner", ("name", "partner_tier")),
    TranslationTarget("Certificate", "certificate", ("title", "description", "certificate_type", "issuer")),
    TranslationTarget("Accreditation", "accreditation", ("title", "description")),
    TranslationTarget("Standard", "standard", ("title", "description")),
    TranslationTarget("Compliance Block", "complianceblock", ("title", "description")),
    TranslationTarget("Trust Metric", "trustmetric", ("title", "value", "description")),
    TranslationTarget("Testimonial", "testimonial", ("quote", "person_designation")),
    TranslationTarget("Document", "downloaddocument", ("title", "description", "file_type")),
    TranslationTarget("Document CTA", "documentpagecta", ("title", "subtitle", "button_text")),
    TranslationTarget("Career Page Settings", "careerpagesettings", ("eyebrow", "hero_title", "hero_subtitle", "hero_primary_button_text", "hero_secondary_button_text", "meta_title", "meta_description", "intro_eyebrow", "intro_title", "intro_text", "empty_jobs_title", "empty_jobs_text", "benefits_eyebrow", "benefits_title", "benefits_text", "process_eyebrow", "process_title", "process_text", "form_help_title", "form_help_text", "application_guide_title", "application_guide_text", "applicant_profile_title", "applicant_profile_text", "document_upload_title", "document_upload_text", "duplicate_application_title", "duplicate_application_text", "privacy_notice", "success_eyebrow", "success_title", "success_text", "cta_title", "cta_text", "cta_button_text", "email_from_name", "email_verification_subject", "email_verification_body", "interview_email_subject", "interview_email_body", "rejection_email_subject", "rejection_email_body")),
    TranslationTarget("Career Stat", "careerstat", ("value", "label", "description")),
    TranslationTarget("Career Benefit", "careerbenefit", ("title", "description")),
    TranslationTarget("Career Process Step", "careerprocessstep", ("step_number", "title", "description")),
    TranslationTarget("Career Department", "careerdepartment", ("name", "description")),
    TranslationTarget("Job Opening", "jobopening", ("title", "summary", "job_description", "responsibilities", "requirements", "qualifications", "skills", "benefits", "location", "experience_level", "salary_range", "salary_note", "apply_button_text", "seo_title", "seo_description")),
    TranslationTarget("Contact Page Settings", "contactpagesettings", ("eyebrow", "hero_title", "hero_subtitle", "intro_title", "intro_text", "map_eyebrow", "map_title", "map_subtitle", "map_button_text")),
    TranslationTarget("Inquiry Subject", "inquirysubject", ("title",)),
    TranslationTarget("Contact Method", "contactmethod", ("title", "value")),
    TranslationTarget("Office Location", "officelocation", ("name", "address", "city", "country")),
    TranslationTarget("Business Hour", "businesshour", ("day_label", "hours")),
]


def get_target(content_type: str):
    for target in TRANSLATION_TARGETS:
        if target.content_type == content_type:
            return target
    return None


def content_type_choices():
    return [(target.content_type, target.model_label) for target in TRANSLATION_TARGETS]
