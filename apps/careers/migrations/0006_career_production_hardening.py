# Generated for career production hardening.

import apps.careers.models
import apps.careers.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("careers", "0005_interview_invitation_system"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jobapplication",
            name="cv",
            field=models.FileField(
                help_text="Required CV / resume file. PDF, DOC or DOCX only.",
                upload_to=apps.careers.models.application_file_path,
                validators=[apps.careers.validators.validate_career_cv_file],
            ),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="supporting_document",
            field=models.FileField(
                blank=True,
                help_text="Optional PDF, DOC or DOCX document.",
                null=True,
                upload_to=apps.careers.models.application_file_path,
                validators=[apps.careers.validators.validate_career_document_file],
            ),
        ),
        migrations.AlterField(
            model_name="jobapplication",
            name="certificate_document",
            field=models.FileField(
                blank=True,
                help_text="Optional PDF, DOC or DOCX certificate/license document.",
                null=True,
                upload_to=apps.careers.models.application_file_path,
                validators=[apps.careers.validators.validate_career_document_file],
            ),
        ),
        migrations.AlterField(
            model_name="jobapplicationdocument",
            name="file",
            field=models.FileField(
                help_text="PDF, DOC or DOCX only.",
                upload_to=apps.careers.models.application_extra_document_path,
                validators=[apps.careers.validators.validate_career_document_file],
            ),
        ),
    ]
