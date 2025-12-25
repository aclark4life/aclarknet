from django.contrib.admin.apps import AdminConfig
from django.contrib.auth.apps import AuthConfig
from django.contrib.contenttypes.apps import ContentTypesConfig
from wagtail.apps import WagtailAppConfig
from taggit.apps import TaggitAppConfig


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
