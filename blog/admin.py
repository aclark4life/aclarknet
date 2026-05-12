from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import Entry


class EntryResource(ModelResource):
    class Meta:
        model = Entry
        import_id_fields = ["pub_date", "slug"]
        fields = ("title", "slug", "pub_date", "body", "tags", "source", "status")

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [str(h).lower().strip() for h in dataset.headers]


def publish_entries(modeladmin, request, queryset):
    queryset.update(status=Entry.PUBLISHED)


publish_entries.short_description = "Mark selected entries as Published"


def draft_entries(modeladmin, request, queryset):
    queryset.update(status=Entry.DRAFT)


draft_entries.short_description = "Mark selected entries as Draft"


@admin.register(Entry)
class EntryAdmin(ImportExportModelAdmin):
    resource_class = EntryResource
    list_display = ["title", "pub_date", "status", "tags", "source"]
    list_filter = ["status", "source", "pub_date"]
    search_fields = ["title", "tags", "body"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "pub_date"
    actions = [publish_entries, draft_entries]
    list_editable = ["status"]
