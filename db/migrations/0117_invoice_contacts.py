# Generated by Django 4.2.1 on 2023-05-12 16:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0116_rename_account_lead"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="contacts",
            field=models.ManyToManyField(blank=True, to="db.contact"),
        ),
    ]
