# Generated by Django 3.0.7 on 2020-07-18 18:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0051_note_doc_type")]

    operations = [
        migrations.AddField(
            model_name="note",
            name="_note",
            field=models.ManyToManyField(
                blank=True, limit_choices_to={"active": True}, to="db.Note"
            ),
        )
    ]
