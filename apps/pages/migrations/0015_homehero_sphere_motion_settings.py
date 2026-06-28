from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0014_merge_20260626_2237"),
    ]

    operations = [
        migrations.AddField(
            model_name="homehero",
            name="sphere_auto_speed",
            field=models.FloatField(
                default=0.24,
                help_text="Base automatic sphere rotation speed. Higher is faster. Current production default: 0.24.",
            ),
        ),
        migrations.AddField(
            model_name="homehero",
            name="sphere_scroll_speed",
            field=models.FloatField(
                default=0.03,
                help_text="Mouse wheel/manual rotation sensitivity. Higher lets users rotate the sphere faster. Current production default: 0.03.",
            ),
        ),
        migrations.AddField(
            model_name="homehero",
            name="sphere_settle_seconds",
            field=models.FloatField(
                default=10.0,
                help_text="Approximate seconds for the sphere to settle back to the clean default X angle after manual rotation.",
            ),
        ),
        migrations.AddField(
            model_name="homehero",
            name="sphere_max_boost",
            field=models.FloatField(
                default=0.55,
                help_text="Maximum temporary auto-rotation speed boost after fast manual scrolling. Higher feels more energetic.",
            ),
        ),
    ]
