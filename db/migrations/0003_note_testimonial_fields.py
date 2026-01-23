# Generated manually for testimonial feature

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0002_client_featured_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="is_testimonial",
            field=models.BooleanField(
                default=False,
                help_text="Check to display this note as a testimonial on the public site",
            ),
        ),
        migrations.AddField(
            model_name="note",
            name="title",
            field=models.CharField(
                blank=True,
                help_text="Title/position of the person giving the testimonial (e.g., 'CEO', 'Project Manager')",
                max_length=300,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="note",
            name="is_featured",
            field=models.BooleanField(
                default=False,
                help_text="Check to feature this testimonial on the homepage",
            ),
        ),
    ]
