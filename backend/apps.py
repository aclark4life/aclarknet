from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.sites.apps import SitesConfig
from django.db import models

from django_mongodb_backend.fields import ObjectIdAutoField
from allauth.account.apps import AccountConfig
from allauth.socialaccount.apps import SocialAccountConfig
from explorer.apps import ExplorerAppConfig
from puput.apps import PuputAppConfig
from taggit.apps import TaggitAppConfig
from wagtail.admin.apps import WagtailAdminAppConfig
from wagtail.documents.apps import WagtailDocsAppConfig
from wagtail.embeds.apps import WagtailEmbedsAppConfig
from wagtail.images.apps import WagtailImagesAppConfig
from wagtail.users.apps import WagtailUsersAppConfig
from wagtail.contrib.forms.apps import WagtailFormsAppConfig
from wagtail.contrib.redirects.apps import WagtailRedirectsAppConfig
from wagtail.apps import WagtailAppConfig
from wagtailmenus.apps import WagtailMenusConfig
from wagtailseo.apps import WagtailSeoConfig


class CustomAdminConfig(AdminConfig):
    default_site = "backend.admin.CustomAdminSite"
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAccountConfig(AccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoSocialAccountConfig(SocialAccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoSitesConfig(SitesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoTaggitAppConfig(TaggitAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoExplorerConfig(ExplorerAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoPuputConfig(PuputAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailAdminAppConfig(WagtailAdminAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailCoreAppConfig(WagtailAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

    def ready(self):
        super().ready()
        try:
            from wagtail.search.models import IndexEntry
        except Exception:
            # If Wagtail's IndexEntry model is unavailable for any reason, just exit.
            return

        id_field = IndexEntry._meta.get_field("id")
        if isinstance(id_field, models.AutoField) and not isinstance(
            id_field, ObjectIdAutoField
        ):
            # Ensure the primary key field uses ObjectIdAutoField with MongoDB.
            id_field.__class__ = ObjectIdAutoField


class MongoWagtailDocsAppConfig(WagtailDocsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailEmbedsAppConfig(WagtailEmbedsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailFormsAppConfig(WagtailFormsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailImagesAppConfig(WagtailImagesAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailRedirectsAppConfig(WagtailRedirectsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailUsersAppConfig(WagtailUsersAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailMenusConfig(WagtailMenusConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailSEOAppConfig(WagtailSeoConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
