# Generated by Django 2.1.10 on 2019-07-07 21:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("db", "0027_remove_project_note")]

    operations = [
        migrations.RenameField(
            model_name="time", old_name="log", new_name="description"
        )
    ]
