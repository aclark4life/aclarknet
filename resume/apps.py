from django.apps import AppConfig


class ResumeConfig(AppConfig):
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"
    name = "resume"
