# Generated by Django 3.1.4 on 2021-01-22 21:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0080_remove_task_billable")]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="db.company",
            ),
        )
    ]
