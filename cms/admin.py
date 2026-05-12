"""CMS admin."""

from django import forms
from django.contrib import admin
from django.db import models

from .models import NowEntry


@admin.register(NowEntry)
class NowEntryAdmin(admin.ModelAdmin):
    list_display = ("__str__", "updated_at", "location")
    list_filter = ("updated_at",)
    ordering = ("-updated_at",)
    fields = ("updated_at", "location", "body")
    formfield_overrides = {
        models.TextField: {
            "widget": forms.Textarea(
                attrs={"rows": 25, "cols": 80, "style": "font-family: monospace;"}
            )
        }
    }
