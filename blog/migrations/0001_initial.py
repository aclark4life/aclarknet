from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Entry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=300)),
                ("slug", models.SlugField(max_length=300)),
                ("pub_date", models.DateField()),
                ("body", models.TextField(blank=True)),
                (
                    "tags",
                    models.CharField(
                        blank=True,
                        help_text="Comma-separated list of tags/categories",
                        max_length=500,
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        blank=True,
                        help_text="Source repo (e.g. blog-2017)",
                        max_length=100,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "entries",
                "ordering": ["-pub_date"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="entry",
            unique_together={("pub_date", "slug")},
        ),
    ]
