# Generated by Django 3.1.7 on 2021-04-11 15:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0094_testimonial")]

    operations = [
        migrations.CreateModel(
            name="Service",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True)),
                ("publish", models.BooleanField(default=False)),
                ("name", models.CharField(blank=True, max_length=300, null=True)),
                ("description", models.TextField(blank=True, null=True)),
            ],
            options={"ordering": ["name"]},
        )
    ]
