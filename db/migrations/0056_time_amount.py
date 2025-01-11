# Generated by Django 3.1.4 on 2021-01-07 17:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0055_auto_20210103_1801")]

    operations = [
        migrations.AddField(
            model_name="time",
            name="amount",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=12, null=True
            ),
        )
    ]
