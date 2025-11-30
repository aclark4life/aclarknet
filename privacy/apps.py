from django.apps import AppConfig


class PrivacyConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "privacy"
