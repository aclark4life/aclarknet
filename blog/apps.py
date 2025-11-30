from django.apps import AppConfig


class BlogConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "blog"
