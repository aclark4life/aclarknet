# Generated by Django 3.0.4 on 2020-03-09 20:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0033_auto_20200201_1329")]

    operations = [
        migrations.AddField(
            model_name="taskorder",
            name="name",
            field=models.CharField(blank=True, max_length=300, null=True),
        )
    ]
