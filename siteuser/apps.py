from django.apps import AppConfig


class SiteuserConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "siteuser"
