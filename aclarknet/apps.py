from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from django.contrib.sites.apps import SitesConfig
from wagtail.apps import WagtailAppConfig
from taggit.apps import TaggitAppConfig
from allauth.account.apps import AccountConfig
from allauth.socialaccount.apps import SocialAccountConfig
from wagtail.admin.apps import WagtailAdminAppConfig
from wagtail.documents.apps import WagtailDocsAppConfig
from wagtail.images.apps import WagtailImagesAppConfig
from wagtail.embeds.apps import WagtailEmbedsAppConfig
from wagtail.contrib.forms.apps import WagtailFormsAppConfig
from wagtail.contrib.redirects.apps import WagtailRedirectsAppConfig
from wagtail.search.apps import WagtailSearchAppConfig
from wagtail.users.apps import WagtailUsersAppConfig


class AdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class AuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class ContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class SitesConfig(SitesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailConfig(WagtailAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class TaggitConfig(TaggitAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class AccountConfig(AccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class SocialAccountConfig(SocialAccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailAdminConfig(WagtailAdminAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailDocsConfig(WagtailDocsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailImagesConfig(WagtailImagesAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailEmbedsConfig(WagtailEmbedsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailFormsConfig(WagtailFormsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailRedirectsConfig(WagtailRedirectsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailSearchConfig(WagtailSearchAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class WagtailUsersConfig(WagtailUsersAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
