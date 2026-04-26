from django.apps import AppConfig


class DBConfig(AppConfig):
    name = "db"
    default_auto_field = "django_mongodb_backend.fields.ObjectIdAutoField"

    def ready(self):
        import db.signals  # noqa
        from bson import ObjectId
        from telepath import BaseAdapter, ValueNode
        from wagtail.admin.telepath import register as wagtail_register

        class ObjectIdAdapter(BaseAdapter):
            def build_node(self, obj, context):
                return ValueNode(str(obj))

        wagtail_register(ObjectIdAdapter(), ObjectId)
