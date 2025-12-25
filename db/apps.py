from django.apps import AppConfig


class DBConfig(AppConfig):
    name = "db"
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

    def ready(self):
        import db.signals  # noqa
