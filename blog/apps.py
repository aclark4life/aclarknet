from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = "blog"
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
