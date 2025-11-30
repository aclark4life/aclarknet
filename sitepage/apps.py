from django.apps import AppConfig


class SitepageConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "sitepage"
