# Generated migration to add default_task fields to Project and Profile

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0002_assign_default_task_to_existing_times'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='default_task',
            field=models.ForeignKey(
                blank=True,
                help_text="Default task for this user's time entries",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='profile_defaults',
                to='db.task'
            ),
        ),
        migrations.AddField(
            model_name='project',
            name='default_task',
            field=models.ForeignKey(
                blank=True,
                help_text="Default task for this project's time entries",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='project_defaults',
                to='db.task'
            ),
        ),
    ]
