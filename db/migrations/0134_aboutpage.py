# Generated by Django 5.0 on 2024-01-03 14:56

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0133_alter_homepage_options_homepage_marketing_blocks"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
    ]

    operations = [
        migrations.CreateModel(
            name="AboutPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "marketing_blocks",
                    wagtail.fields.StreamField(
                        [
                            (
                                "marketing_block",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "title",
                                            wagtail.blocks.CharBlock(
                                                help_text="Enter the block title",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "content",
                                            wagtail.blocks.RichTextBlock(
                                                help_text="Enter the block content",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "images",
                                            wagtail.blocks.ListBlock(
                                                wagtail.images.blocks.ImageChooserBlock(
                                                    required=False
                                                ),
                                                help_text="Select one or two images for column display. Select three or more images for carousel display.",
                                            ),
                                        ),
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                help_text="Select one image for background display.",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "block_class",
                                            wagtail.blocks.CharBlock(
                                                default="vh-100 app-ribbon",
                                                form_classname="full title",
                                                help_text="Enter a CSS class for styling the marketing block",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "image_class",
                                            wagtail.blocks.CharBlock(
                                                default="img-thumbnail p-5",
                                                form_classname="full title",
                                                help_text="Enter a CSS class for styling the column display image(s)",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "layout_class",
                                            wagtail.blocks.CharBlock(
                                                default="d-flex flex-row",
                                                form_classname="full title",
                                                help_text="Enter a CSS class for styling the layout.",
                                                required=False,
                                            ),
                                        ),
                                    ]
                                ),
                            )
                        ],
                        blank=True,
                        null=True,
                        use_json_field=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "About Page",
            },
            bases=("wagtailcore.page",),
        ),
    ]
