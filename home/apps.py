from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        # Wagtail 8.0's preview REST API v3 (built on django-ninja) builds
        # pydantic schemas for every model's primary key at app-registry
        # startup. django-ninja doesn't know about MongoDB's
        # ObjectIdAutoField (from django-mongodb-backend), so without this
        # registration Django fails to start entirely. "home" is the first
        # app in INSTALLED_APPS, so this runs before Wagtail's apps.
        from ninja.orm import register_field

        register_field("ObjectIdAutoField", str)
