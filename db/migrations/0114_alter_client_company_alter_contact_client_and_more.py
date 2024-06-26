# Generated by Django 4.2.1 on 2023-05-09 16:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("db", "0113_homepage_remove_account_ignore_remove_account_note_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="company",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.company",
            ),
        ),
        migrations.AlterField(
            model_name="contact",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.client",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.client",
            ),
        ),
        migrations.AlterField(
            model_name="invoice",
            name="project",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.project",
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="client",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.client",
            ),
        ),
        migrations.AlterField(
            model_name="time",
            name="client",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"active": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.client",
            ),
        ),
        migrations.AlterField(
            model_name="time",
            name="project",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"active": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.project",
            ),
        ),
    ]
