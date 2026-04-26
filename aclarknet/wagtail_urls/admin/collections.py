# Copied from wagtail/admin/urls/collections.py (Wagtail 7.3.1)
# All <int: path converters replaced with <str: for Django MongoDB Backend compatibility.
# Re-diff against upstream on Wagtail upgrades.
from django.urls import path

from wagtail.admin.views import collection_privacy, collections

app_name = "wagtailadmin_collections"
urlpatterns = [
    path("", collections.Index.as_view(), name="index"),
    path("add/", collections.Create.as_view(), name="add"),
    path("<str:pk>/", collections.Edit.as_view(), name="edit"),
    path("<str:pk>/delete/", collections.Delete.as_view(), name="delete"),
    path(
        "<str:collection_id>/privacy/",
        collection_privacy.set_privacy,
        name="set_privacy",
    ),
]
