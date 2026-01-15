# Generated manually to remove unused fields from models

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0001_initial"),
    ]

    operations = [
        # Remove unused fields from Client model
        migrations.RemoveField(
            model_name="client",
            name="publish",
        ),
        migrations.RemoveField(
            model_name="client",
            name="link",
        ),
        # Remove unused field from Company model
        migrations.RemoveField(
            model_name="company",
            name="ein",
        ),
        # Remove unused fields from Project model
        migrations.RemoveField(
            model_name="project",
            name="draggable_positions",
        ),
        migrations.RemoveField(
            model_name="project",
            name="github_project",
        ),
        migrations.RemoveField(
            model_name="project",
            name="github_repository",
        ),
        # Remove unused field from Testimonial model
        migrations.RemoveField(
            model_name="testimonial",
            name="slug",
        ),
    ]
