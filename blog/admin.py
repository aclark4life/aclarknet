from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import Entry


class EntryResource(ModelResource):
    class Meta:
        model = Entry
        import_id_fields = ["pub_date", "slug"]
        fields = ("title", "slug", "pub_date", "body", "tags", "source")

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [str(h).lower().strip() for h in dataset.headers]


@admin.register(Entry)
class EntryAdmin(ImportExportModelAdmin):
    resource_class = EntryResource
    list_display = ["title", "pub_date", "tags", "source"]
    list_filter = ["source", "pub_date"]
    search_fields = ["title", "tags", "body"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "pub_date"
