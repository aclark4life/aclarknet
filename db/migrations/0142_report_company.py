# Generated by Django 5.0 on 2024-01-11 23:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0141_auto_20240111_0149"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.company",
            ),
        ),
    ]
