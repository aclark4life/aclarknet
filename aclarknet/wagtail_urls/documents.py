# Copied from wagtail/documents/urls.py (Wagtail 7.3.1)
# All <int: path converters replaced with <str: for Django MongoDB Backend compatibility.
# Re-diff against upstream on Wagtail upgrades.
from django.urls import path, re_path

from wagtail.documents.views import serve

urlpatterns = [
    re_path(r"^(\d+)/(.*)$", serve.serve, name="wagtaildocs_serve"),
    path(
        "authenticate_with_password/<str:restriction_id>/",
        serve.authenticate_with_password,
        name="wagtaildocs_authenticate_with_password",
    ),
]
