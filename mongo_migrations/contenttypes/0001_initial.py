# Generated by Django 5.0.11.dev20250107212806 on 2025-01-10 02:46

import django.contrib.contenttypes.models
import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ContentType",
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
                ("app_label", models.CharField(max_length=100)),
                (
                    "model",
                    models.CharField(
                        max_length=100, verbose_name="python model class name"
                    ),
                ),
            ],
            options={
                "verbose_name": "content type",
                "verbose_name_plural": "content types",
                "db_table": "django_content_type",
                "unique_together": {("app_label", "model")},
            },
            managers=[
                ("objects", django.contrib.contenttypes.models.ContentTypeManager()),
            ],
        ),
    ]
