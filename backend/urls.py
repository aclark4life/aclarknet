from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include
from django.contrib import admin
from .views import BaseView


urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("django/", admin.site.urls),
    path("wagtail/", include("wagtail.admin.urls")),
    path("dashboard/", include("db.urls")),
    path("hijack/", include("hijack.urls")),
    path("user/", include("siteuser.urls")),
    path("", BaseView.as_view(), name="base")
] + debug_toolbar_urls()
