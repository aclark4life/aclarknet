# Generated by Django 4.0.5 on 2022-08-03 15:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0108_alter_time_invoice"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="client",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="company",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="contact",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="expense",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="invoice",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="note",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="profile",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="project",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="report",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="service",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="task",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="testimonial",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="time",
            name="ignore",
            field=models.BooleanField(default=False),
        ),
    ]
