"""Tests for related fields configuration in base views."""

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.views.generic import DetailView

from db.forms import ClientForm
from db.models import Client
from db.views.base import BaseView

User = get_user_model()


class TestRelatedView(BaseView, DetailView):
    """Test view that uses BaseView with related configuration."""

    model = Client
    form_class = ClientForm


class CustomRelatedView(BaseView, DetailView):
    """Test view with custom related field configuration."""

    model = Client
    form_class = ClientForm
    related_title_fields = ["name", "url"]  # Custom title fields
    related_excluded_fields = ["type", "id", "item", "description"]  # Custom exclusions


class RelatedFieldsConfigTest(TestCase):
    """Test that related field configuration is passed to template context."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpass", is_superuser=True
        )
        self.client_obj = Client.objects.create(
            name="Test Client", description="Test Description", url="http://test.com"
        )

    def test_default_related_title_fields(self):
        """Test that default related_title_fields are set on BaseView."""
        view = TestRelatedView()
        self.assertEqual(
            view.related_title_fields, ["name", "title", "subject", "description"]
        )

    def test_default_related_excluded_fields(self):
        """Test that default related_excluded_fields are set on BaseView."""
        view = TestRelatedView()
        self.assertEqual(view.related_excluded_fields, ["type", "id", "item"])

    def test_custom_related_configuration(self):
        """Test that custom related field configuration can be set on subclasses."""
        view = CustomRelatedView()
        self.assertEqual(view.related_title_fields, ["name", "url"])
        self.assertEqual(
            view.related_excluded_fields, ["type", "id", "item", "description"]
        )

    def test_related_config_passed_to_context(self):
        """Test that related field configuration is passed to template context when has_related is True."""
        request = self.factory.get("/")
        request.user = self.user

        view = TestRelatedView()
        view.request = request
        view.object = self.client_obj
        view.kwargs = {"pk": self.client_obj.pk}
        view.has_related = True
        view._queryset_related = []

        context = view.get_context_data()

        # Check that configuration is in context
        self.assertIn("related_title_fields", context)
        self.assertIn("related_excluded_fields", context)
        self.assertEqual(
            context["related_title_fields"], ["name", "title", "subject", "description"]
        )
        self.assertEqual(context["related_excluded_fields"], ["type", "id", "item"])

    def test_custom_related_config_passed_to_context(self):
        """Test that custom related field configuration is passed to template context."""
        request = self.factory.get("/")
        request.user = self.user

        view = CustomRelatedView()
        view.request = request
        view.object = self.client_obj
        view.kwargs = {"pk": self.client_obj.pk}
        view.has_related = True
        view._queryset_related = []

        context = view.get_context_data()

        # Check that custom configuration is in context
        self.assertEqual(context["related_title_fields"], ["name", "url"])
        self.assertEqual(
            context["related_excluded_fields"], ["type", "id", "item", "description"]
        )

    def test_related_config_not_in_context_without_has_related(self):
        """Test that related configuration is NOT added to context when has_related is False."""
        request = self.factory.get("/")
        request.user = self.user

        view = TestRelatedView()
        view.request = request
        view.object = self.client_obj
        view.kwargs = {"pk": self.client_obj.pk}
        view.has_related = False

        context = view.get_context_data()

        # Check that configuration is NOT in context when has_related is False
        self.assertNotIn("related_title_fields", context)
        self.assertNotIn("related_excluded_fields", context)
