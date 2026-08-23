from django.db import migrations
from django.utils import timezone


ADDRESS = "6619, King Fahd Road, Office - 05, Dammam - 32243 - 3404, KSA"


def apply_production_content(apps, schema_editor):
    CompanyProfile = apps.get_model("core", "CompanyProfile")
    LocalizedContent = apps.get_model("core", "LocalizedContent")
    OfficeLocation = apps.get_model("core", "OfficeLocation")
    CareerBenefit = apps.get_model("careers", "CareerBenefit")
    CareerDepartment = apps.get_model("careers", "CareerDepartment")
    CareerProcessStep = apps.get_model("careers", "CareerProcessStep")
    CareerStat = apps.get_model("careers", "CareerStat")
    JobOpening = apps.get_model("careers", "JobOpening")
    ContactPageSettings = apps.get_model("inquiries", "ContactPageSettings")
    FAQ = apps.get_model("pages", "FAQ")

    CompanyProfile.objects.update(address=ADDRESS, city="Dammam", country="Saudi Arabia")

    office = OfficeLocation.objects.filter(is_primary=True).first() or OfficeLocation.objects.first()
    if office is None:
        office = OfficeLocation(name="Main Office")
    office.address = ADDRESS
    # The address already includes the city and country; blank these fields to
    # prevent the contact card and footer from repeating them.
    office.city = ""
    office.country = ""
    office.is_primary = True
    office.is_active = True
    office.save()
    LocalizedContent.objects.filter(
        content_type="officelocation", object_id=office.pk, field_name__in=["address", "city", "country"]
    ).delete()

    ContactPageSettings.objects.update(map_subtitle=ADDRESS)
    FAQ.objects.filter(question__icontains="updated from admin").delete()
    FAQ.objects.filter(answer__icontains="Django admin").delete()

    department, _ = CareerDepartment.objects.update_or_create(
        slug="engineering",
        defaults={
            "name": "Electrical Engineering",
            "description": "Electrical engineering, power systems and specialist cable-services roles.",
            "sort_order": 1,
            "is_active": True,
        },
    )
    CareerDepartment.objects.exclude(pk=department.pk).update(is_active=False)

    now = timezone.now()
    jobs = [
        {
            "slug": "electrical-engineer",
            "title": "Electrical Engineer",
            "job_code": "SES-ENG-001",
            "job_level": "mid",
            "experience_level": "3+ years",
            "summary": "Coordinate electrical engineering activities, review technical documents and support safe project execution.",
            "job_description": "The Electrical Engineer supports project planning, technical review, site coordination, material follow-up and progress reporting for SESCCO projects.\n\nThe role requires sound electrical engineering knowledge, practical judgment, safety awareness and professional communication with project stakeholders.",
            "responsibilities": "Coordinate daily site electrical activities.\nReview drawings, material requirements and work fronts.\nCoordinate with supervisors, QA/QC and client representatives.\nPrepare progress updates and support safe work execution.",
            "requirements": "Bachelor's degree in Electrical Engineering.\nMinimum 3 years of relevant project or site experience.\nStrong knowledge of electrical drawings, materials and site coordination.\nGood communication and technical documentation skills.",
            "qualifications": "Recognized electrical engineering qualification.\nSaudi project experience is preferred.\nAbility to interpret drawings, specifications and technical documents.",
            "skills": "Site coordination.\nDrawing review.\nDaily reporting.\nSafety communication.",
            "benefits": "Competitive package according to experience.\nProfessional project environment.\nOpportunity to work on industrial and infrastructure projects.",
            "sort_order": 1,
        },
        {
            "slug": "mv-cable-splicer",
            "title": "MV Cable Splicer",
            "job_code": "SES-ELC-002",
            "job_level": "senior",
            "experience_level": "5+ years",
            "summary": "Perform medium-voltage cable jointing, termination and testing in accordance with approved procedures and safety standards.",
            "job_description": "The MV Cable Splicer performs installation, jointing and termination of medium-voltage power cables for industrial and infrastructure projects.\n\nThe role requires proven field competence, strict adherence to manufacturer instructions and safety procedures, and accurate completion of testing and work records.",
            "responsibilities": "Prepare, splice and terminate MV cables using approved kits and procedures.\nInspect cable condition and verify phase identification before work.\nSupport insulation, continuity and commissioning tests.\nMaintain tools, jointing materials and accurate work records.\nComply with permit-to-work, quality and safety requirements.",
            "requirements": "Minimum 5 years of relevant MV cable jointing and termination experience.\nDemonstrated experience with common MV cable types and accessories.\nAbility to read cable schedules, drawings and manufacturer instructions.\nStrong safety awareness and attention to detail.",
            "qualifications": "Recognized MV cable splicing or jointing certification.\nManufacturer certification is preferred.\nSaudi industrial or utility project experience is an advantage.",
            "skills": "MV cable jointing.\nCable termination.\nCable preparation and testing.\nTechnical documentation.\nSafe work practices.",
            "benefits": "Competitive package according to qualifications and experience.\nProfessional project environment.\nOpportunity to support major industrial and infrastructure projects.",
            "sort_order": 2,
        },
    ]

    retained_ids = []
    for data in jobs:
        slug = data.pop("slug")
        summary = data["summary"]
        job, _ = JobOpening.objects.update_or_create(
            slug=slug,
            defaults={
                **data,
                "department": department,
                "location": "Dammam, Saudi Arabia",
                "employment_type": "full_time",
                "work_mode": "site",
                "positions_available": 1,
                "salary_range": "",
                "show_salary": False,
                "apply_button_text": "Apply Now",
                "status": "published",
                "is_featured": True,
                "is_active": True,
                "published_at": now,
                "closed_at": None,
                "seo_title": f"{data['title']} | SESCCO Careers",
                "seo_description": summary[:250],
            },
        )
        retained_ids.append(job.pk)

    JobOpening.objects.exclude(pk__in=retained_ids).update(
        status="closed", is_active=False, closed_at=now
    )

    CareerStat.objects.exclude(label__in=["Open positions", "Online application", "Interview invite"]).update(is_active=False)
    for order, (value, label, description, icon) in enumerate(
        [
            ("2", "Open positions", "Current opportunities for qualified electrical professionals.", "▣"),
            ("100%", "Online application", "Applicants can submit CVs and documents directly from the job page.", "↗"),
            ("Email", "Interview invite", "Shortlisted applicants receive official invitation details by email.", "✉"),
        ],
        1,
    ):
        CareerStat.objects.update_or_create(
            label=label,
            defaults={"value": value, "description": description, "icon_text": icon, "show_on_hero": True, "sort_order": order, "is_active": True},
        )

    CareerBenefit.objects.filter(title="Clear review workflow").update(
        description="Applications, documents and interview invitations follow a structured and professional recruitment process."
    )
    CareerProcessStep.objects.filter(step_number="02").update(
        title="HR Review",
        description="Our HR team assesses each application against the role requirements.",
        is_active=True,
    )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0013_exact_google_maps_location"),
        ("careers", "0009_career_contact_context"),
        ("inquiries", "0003_contact_email_notifications"),
        ("pages", "0015_homehero_sphere_motion_settings"),
    ]

    operations = [
        migrations.RunPython(apply_production_content, migrations.RunPython.noop),
    ]
