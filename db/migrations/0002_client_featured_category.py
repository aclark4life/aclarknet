# Generated manually for client categorization feature

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="featured",
            field=models.BooleanField(
                default=False,
                help_text="Check to display this client on the public clients page",
            ),
        ),
        migrations.AddField(
            model_name="client",
            name="category",
            field=models.CharField(
                blank=True,
                choices=[
                    ("government", "Government"),
                    ("non-profit", "Non-Profit"),
                    ("private", "Private Sector"),
                    ("education", "Education"),
                    ("healthcare", "Healthcare"),
                    ("other", "Other"),
                ],
                help_text="Client category for grouping on the public clients page",
                max_length=50,
                null=True,
            ),
        ),
    ]
