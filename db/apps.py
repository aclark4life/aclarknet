from django.apps import AppConfig


class DbConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "db"
    verbose_name = "DB"
