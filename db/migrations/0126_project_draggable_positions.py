# Generated by Django 4.2.1 on 2023-06-11 18:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0125_report_reports"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="draggable_positions",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
