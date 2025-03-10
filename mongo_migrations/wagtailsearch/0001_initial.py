# Generated by Django 5.0.11.dev20250107212806 on 2025-01-10 02:40

import django.db.models.deletion
import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="IndexEntry",
            fields=[
                (
                    "id",
                    django_mongodb_backend.fields.ObjectIdAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("object_id", models.CharField(max_length=50)),
                ("title_norm", models.FloatField(default=1.0)),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "index entry",
                "verbose_name_plural": "index entries",
                "abstract": False,
                "unique_together": {("content_type", "object_id")},
            },
        ),
    ]
