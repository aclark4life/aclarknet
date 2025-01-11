# Generated by Django 3.1.4 on 2021-01-24 22:52

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("taggit", "0003_taggeditem_add_unique_index"),
        ("db", "0082_client_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="client",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        )
    ]
