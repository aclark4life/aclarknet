# Copied from wagtail/admin/urls/editing_sessions.py (Wagtail 7.3.1)
# All <int: path converters replaced with <str: for Django MongoDB Backend compatibility.
# Re-diff against upstream on Wagtail upgrades.
from django.urls import path

from wagtail.admin.views.editing_sessions import ping, release

app_name = "wagtailadmin_editing_sessions"
urlpatterns = [
    path(
        "ping/<str:app_label>/<str:model_name>/<str:object_id>/<str:session_id>/",
        ping,
        name="ping",
    ),
    path(
        "release/<str:session_id>/",
        release,
        name="release",
    ),
]
