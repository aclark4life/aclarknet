# Generated by Django 2.1.7 on 2019-02-23 21:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0006_auto_20181110_2202")]

    operations = [
        migrations.AddField(
            model_name="estimate",
            name="note",
            field=models.ManyToManyField(
                blank=True, limit_choices_to={"active": True}, to="db.Note"
            ),
        )
    ]
