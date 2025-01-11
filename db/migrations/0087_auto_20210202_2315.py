# Generated by Django 3.1.4 on 2021-02-02 23:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0086_invoice_user")]

    operations = [
        migrations.AddField(
            model_name="project",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="note",
            field=models.ManyToManyField(blank=True, to="db.Note"),
        ),
    ]
