from django.db import models
from django.urls import reverse


class Entry(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300)
    pub_date = models.DateField()
    body = models.TextField(blank=True)
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated list of tags/categories",
    )
    source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Source repo (e.g. blog-2017)",
    )

    class Meta:
        ordering = ["-pub_date"]
        unique_together = [("pub_date", "slug")]
        verbose_name_plural = "entries"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "blog:entry_detail",
            kwargs={
                "year": self.pub_date.year,
                "month": f"{self.pub_date.month:02d}",
                "day": f"{self.pub_date.day:02d}",
                "slug": self.slug,
            },
        )

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
