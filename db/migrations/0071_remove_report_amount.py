# Generated by Django 3.1.4 on 2021-01-19 22:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("db", "0070_report_amount")]

    operations = [migrations.RemoveField(model_name="report", name="amount")]
