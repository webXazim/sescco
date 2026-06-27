from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='client_logo',
            field=models.ImageField(blank=True, null=True, upload_to='projects/stakeholders/'),
        ),
        migrations.AddField(
            model_name='project',
            name='contractor_logo',
            field=models.ImageField(blank=True, null=True, upload_to='projects/stakeholders/'),
        ),
    ]
