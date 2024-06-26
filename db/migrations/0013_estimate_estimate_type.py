# Generated by Django 2.1.8 on 2019-05-06 10:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0012_delete_newsletter")]

    operations = [
        migrations.AddField(
            model_name="estimate",
            name="estimate_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("1x", "Small"),
                    ("2x", "Medium"),
                    ("3x", "Large"),
                    ("4x", "XL"),
                    ("5x", "XXL"),
                ],
                max_length=255,
                null=True,
            ),
        )
    ]
