# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


def assign_default_task_to_times(apps, schema_editor):
    """Assign the default task to all existing Time entries that don't have a task."""
    Time = apps.get_model("db", "Time")
    Task = apps.get_model("db", "Task")

    # Get or create the default task
    default_task, created = Task.objects.get_or_create(
        name="Default Task",
        defaults={
            "rate": None,
            "unit": 1.0,
        },
    )

    # Update all Time entries without a task
    times_without_task = Time.objects.filter(task__isnull=True)
    count = times_without_task.count()

    if count > 0:
        times_without_task.update(task=default_task)
        print(f"Updated {count} time entries with the default task.")
    else:
        print("No time entries needed updating.")


def reverse_assign_default_task(apps, schema_editor):
    """Reverse migration - remove default task from time entries that have it."""
    Time = apps.get_model("db", "Time")
    Task = apps.get_model("db", "Task")

    # Find the default task
    try:
        default_task = Task.objects.get(name="Default Task")
        # Set task to None for all Time entries that have the default task
        Time.objects.filter(task=default_task).update(task=None)
    except Task.DoesNotExist:
        # If default task doesn't exist, nothing to reverse
        pass


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            assign_default_task_to_times,
            reverse_code=reverse_assign_default_task,
        ),
        migrations.AddField(
            model_name="profile",
            name="default_task",
            field=models.ForeignKey(
                blank=True,
                help_text="Default task for this user's time entries",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="profile_defaults",
                to="db.task",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="default_task",
            field=models.ForeignKey(
                blank=True,
                help_text="Default task for this project's time entries",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="project_defaults",
                to="db.task",
            ),
        ),
    ]
