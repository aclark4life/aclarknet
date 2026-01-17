"""URL patterns for siteuser app."""

from django.urls import path

from .views import ProfileDetailView, ProfileUpdateView

urlpatterns = [
    path("profile/", ProfileDetailView.as_view(), name="profile_view"),
    path("profile/edit/", ProfileUpdateView.as_view(), name="profile_edit"),
]
