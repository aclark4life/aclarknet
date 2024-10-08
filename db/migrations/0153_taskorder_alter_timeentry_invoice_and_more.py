# Generated by Django 5.1 on 2024-10-05 19:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0152_alter_timeentry_options_alter_timeentry_invoice_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaskOrder",
            fields=[
                (
                    "invoice_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="db.invoice",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("db.invoice",),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"archived": False},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="time_entries",
                to="db.invoice",
            ),
        ),
        migrations.AlterField(
            model_name="timeentry",
            name="task",
            field=models.ForeignKey(
                limit_choices_to={"archived": False},
                on_delete=django.db.models.deletion.CASCADE,
                related_name="time_entries",
                to="db.task",
            ),
        ),
    ]
