# Generated by Django 3.1.4 on 2021-02-05 21:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0087_auto_20210202_2315")]

    operations = [
        migrations.AddField(
            model_name="note", name="pin", field=models.BooleanField(default=False)
        )
    ]
