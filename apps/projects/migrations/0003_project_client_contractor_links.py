from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0002_certificate_description"),
        ("projects", "0002_project_stakeholder_logos"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="client",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="project_client_entries", to="clients.client"),
        ),
        migrations.AddField(
            model_name="project",
            name="contractor",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="project_contractor_entries", to="clients.client"),
        ),
    ]
