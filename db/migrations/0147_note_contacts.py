# Generated by Django 5.0.1 on 2024-01-18 22:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0146_report_team"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="contacts",
            field=models.ManyToManyField(blank=True, to="db.contact"),
        ),
    ]
