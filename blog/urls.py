from django.urls import path

from .views import EntryDetailView, EntryListView

app_name = "blog"

urlpatterns = [
    path("", EntryListView.as_view(), name="entry_list"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:slug>/",
        EntryDetailView.as_view(),
        name="entry_detail",
    ),
]
