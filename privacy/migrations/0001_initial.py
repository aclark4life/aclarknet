# Generated by Django 5.0.4 on 2024-04-23 17:18

import django.db.models.deletion
import wagtailmarkdown.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("wagtailcore", "0091_remove_revision_submitted_for_moderation"),
    ]

    operations = [
        migrations.CreateModel(
            name="PrivacyPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("body", wagtailmarkdown.fields.MarkdownField()),
            ],
            options={
                "verbose_name": "Privacy Page",
            },
            bases=("wagtailcore.page",),
        ),
    ]
