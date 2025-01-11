# Generated by Django 2.2.3 on 2019-07-30 18:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0030_company")]

    operations = [
        migrations.AddField(
            model_name="siteconfiguration",
            name="company",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"active": True},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="db.Company",
            ),
        )
    ]
