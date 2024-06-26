# Generated by Django 4.2.1 on 2023-06-23 18:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0127_profile_github_access_token"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="github",
            field=models.URLField(
                blank=True, null=True, verbose_name="GitHub Organization"
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="github",
            field=models.URLField(blank=True, null=True, verbose_name="GitHub Project"),
        ),
    ]
