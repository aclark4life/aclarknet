# Generated by Django 3.1.4 on 2021-01-12 18:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0057_auto_20210107_1756")]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="phone",
            field=models.CharField(blank=True, max_length=300, null=True),
        )
    ]
