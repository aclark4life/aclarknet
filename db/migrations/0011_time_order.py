# Generated by Django 2.2 on 2019-05-02 18:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0010_auto_20190501_2031")]

    operations = [
        migrations.AddField(
            model_name="time",
            name="order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.Order",
            ),
        )
    ]
