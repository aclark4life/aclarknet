"""CMS models."""

import django_mongodb_backend.fields
from django.db import models


class NowEntry(models.Model):
    """A single 'now page' snapshot. Latest entry is shown at /now/."""

    id = django_mongodb_backend.fields.ObjectIdAutoField(
        primary_key=True, serialize=False
    )
    body = models.TextField(help_text="RST-formatted content.")
    updated_at = models.DateField(help_text="Date this entry was written.")
    location = models.CharField(
        max_length=200, blank=True, help_text="e.g. Bethesda, MD, USA"
    )

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Now Entry"
        verbose_name_plural = "Now Entries"

    def __str__(self):
        return f"Now ({self.updated_at})"

    def render_body(self):
        """Render RST body to HTML, falling back to plain text."""
        try:
            from docutils.core import publish_parts

            parts = publish_parts(
                source=self.body,
                writer_name="html",
                settings_overrides={"initial_header_level": 2},
            )
            return parts["body"]
        except Exception:
            return self.body
