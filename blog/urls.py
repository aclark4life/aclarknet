from django.urls import re_path, path

from .views import EntryDetailView, EntryListView

app_name = "blog"

urlpatterns = [
    path("", EntryListView.as_view(), name="entry_list"),
    re_path(
        r"^(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<slug>[-a-zA-Z0-9_.]+)/$",
        EntryDetailView.as_view(),
        name="entry_detail",
    ),
]
