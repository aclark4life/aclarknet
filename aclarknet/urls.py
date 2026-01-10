from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views


# MongoDB Wagtail fixes
urlpatterns = []

urlpatterns += [
    path("admin/", admin.site.urls),
    path("wagtail/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("dashboard/", include("db.urls")),
    path("hijack/", include("hijack.urls")),
    path("accounts/", include("allauth.urls")),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += debug_toolbar_urls()

urlpatterns = (
    urlpatterns
    + [
    ]
)

urlpatterns = urlpatterns + [
    path("", include("cms.urls")),
]
