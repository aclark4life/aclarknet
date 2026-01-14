# Generated manually for adding rate and mail fields to SiteUser

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("siteuser", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="siteuser",
            name="rate",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="User's hourly cost rate for time tracking",
                max_digits=12,
                null=True,
                verbose_name="Hourly Rate",
            ),
        ),
        migrations.AddField(
            model_name="siteuser",
            name="mail",
            field=models.BooleanField(
                default=False,
                help_text="Send email notifications for time entries",
                verbose_name="Email Notifications",
            ),
        ),
    ]
