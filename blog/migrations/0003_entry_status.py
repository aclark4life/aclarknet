from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0002_alter_entry_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="entry",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("published", "Published")],
                db_index=True,
                default="published",
                help_text="Only published entries are visible to the public.",
                max_length=20,
            ),
        ),
    ]
