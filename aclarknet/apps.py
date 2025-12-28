from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from wagtail.apps import WagtailAppConfig
from taggit.apps import TaggitAppConfig
from allauth.account.apps import AccountConfig
from allauth.socialaccount.apps import SocialAccountConfig
from wagtail.admin.apps import WagtailAdminAppConfig
from wagtail.documents.apps import WagtailDocsAppConfig
from wagtail.images.apps import WagtailImagesAppConfig


class MongoAdminConfig(AdminConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAuthConfig(AuthConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoContentTypesConfig(ContentTypesConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailAppConfig(WagtailAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoTaggitAppConfig(TaggitAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoAccountConfig(AccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoSocialAccountConfig(SocialAccountConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailAdminConfig(WagtailAdminAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailDocsConfig(WagtailDocsAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"


class MongoWagtailImagesConfig(WagtailImagesAppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
