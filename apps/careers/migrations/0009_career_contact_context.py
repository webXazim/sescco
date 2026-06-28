from django.db import migrations, models


def apply_career_contact_context(apps, schema_editor):
    CareerPageSettings = apps.get_model("careers", "CareerPageSettings")
    InquirySubject = apps.get_model("inquiries", "InquirySubject")

    CareerPageSettings.objects.filter(hero_secondary_button_url="/contact/").update(
        hero_secondary_button_url="/contact/?type=career"
    )
    CareerPageSettings.objects.filter(cta_button_url="/contact/").update(
        cta_button_url="/contact/?type=career"
    )
    InquirySubject.objects.update_or_create(
        title="Career / HR Inquiry",
        defaults={"email_to": "hr@sescco.com", "sort_order": 6, "is_active": True},
    )


def revert_career_contact_context(apps, schema_editor):
    CareerPageSettings = apps.get_model("careers", "CareerPageSettings")

    CareerPageSettings.objects.filter(hero_secondary_button_url="/contact/?type=career").update(
        hero_secondary_button_url="/contact/"
    )
    CareerPageSettings.objects.filter(cta_button_url="/contact/?type=career").update(
        cta_button_url="/contact/"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("careers", "0008_rename_careers_emai_job_id_56c57d_idx_careers_car_job_id_5da641_idx_and_more"),
        ("inquiries", "0003_contact_email_notifications"),
    ]

    operations = [
        migrations.AlterField(
            model_name="careerpagesettings",
            name="hero_secondary_button_url",
            field=models.CharField(default="/contact/?type=career", max_length=255),
        ),
        migrations.AlterField(
            model_name="careerpagesettings",
            name="cta_button_url",
            field=models.CharField(default="/contact/?type=career", max_length=255),
        ),
        migrations.RunPython(apply_career_contact_context, revert_career_contact_context),
    ]
