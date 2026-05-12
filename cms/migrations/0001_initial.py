import django_mongodb_backend.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NowEntry",
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
                ("body", models.TextField(help_text="RST-formatted content.")),
                (
                    "updated_at",
                    models.DateField(help_text="Date this entry was written."),
                ),
                (
                    "location",
                    models.CharField(
                        blank=True,
                        help_text="e.g. Bethesda, MD, USA",
                        max_length=200,
                    ),
                ),
            ],
            options={
                "verbose_name": "Now Entry",
                "verbose_name_plural": "Now Entries",
                "ordering": ["-updated_at"],
            },
        ),
    ]
