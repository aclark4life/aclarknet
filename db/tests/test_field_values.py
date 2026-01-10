"""Tests for field_values refactoring in base views."""

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.views.generic import DetailView

from db.forms import ClientForm, InvoiceForm
from db.models import Client, Invoice
from db.views.base import BaseView

User = get_user_model()


class TestFieldValuesView(BaseView, DetailView):
    """Test view that uses BaseView with form_class."""

    model = Client
    form_class = ClientForm


class FieldValuesDefaultBehaviorTest(TestCase):
    """Test that field_values shows all fields by default in detail views."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client_obj = Client.objects.create(
            name="Test Client", description="Test Description", url="http://test.com"
        )

    def test_get_field_values_shows_all_form_fields_by_default(self):
        """By default, all form fields should be shown in detail views."""
        request = self.factory.get("/")
        request.user = self.user

        view = TestFieldValuesView()
        view.request = request
        view.object = self.client_obj

        field_values = view.get_field_values()

        # Should return all fields from ClientForm
        field_names = [fv[0] for fv in field_values]
        self.assertIn("name", field_names)
        self.assertIn("description", field_names)
        self.assertIn("url", field_names)

    def test_get_field_values_with_include_filter(self):
        """Test field_values_include filters to only specified fields."""
        request = self.factory.get("/")
        request.user = self.user

        view = TestFieldValuesView()
        view.request = request
        view.object = self.client_obj
        view.field_values_include = ["name", "url"]

        field_values = view.get_field_values()

        field_names = [fv[0] for fv in field_values]
        self.assertIn("name", field_names)
        self.assertIn("url", field_names)
        self.assertNotIn("description", field_names)

    def test_get_field_values_with_exclude_filter(self):
        """Test field_values_exclude removes specified fields."""
        request = self.factory.get("/")
        request.user = self.user

        view = TestFieldValuesView()
        view.request = request
        view.object = self.client_obj
        view.field_values_exclude = ["description"]

        field_values = view.get_field_values()

        field_names = [fv[0] for fv in field_values]
        self.assertIn("name", field_names)
        self.assertIn("url", field_names)
        self.assertNotIn("description", field_names)

    def test_get_field_values_with_extra_fields(self):
        """Test field_values_extra appends additional fields."""
        request = self.factory.get("/")
        request.user = self.user

        view = TestFieldValuesView()
        view.request = request
        view.object = self.client_obj
        view.field_values_extra = [("Custom Field", "Custom Value")]

        field_values = view.get_field_values()

        field_names = [fv[0] for fv in field_values]
        self.assertIn("name", field_names)
        self.assertIn("Custom Field", field_names)

        # Find the custom field value
        custom_value = next(fv[1] for fv in field_values if fv[0] == "Custom Field")
        self.assertEqual(custom_value, "Custom Value")


class FieldValuesListViewTest(TestCase):
    """Test that field_values still works correctly for list views."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.invoice1 = Invoice.objects.create(
            subject="Invoice 1", amount=100.00, cost=50.00, net=50.00, hours=10.0
        )
        self.invoice2 = Invoice.objects.create(
            subject="Invoice 2", amount=200.00, cost=100.00, net=100.00, hours=20.0
        )

    def test_get_field_values_for_list_view(self):
        """Test field_values works correctly for list views (page_obj provided)."""
        request = self.factory.get("/")
        request.user = self.user

        view = TestFieldValuesView()
        view.request = request
        view.form_class = InvoiceForm

        page_obj = [self.invoice1, self.invoice2]
        field_values_page = view.get_field_values(page_obj=page_obj)

        # Should have 2 items
        self.assertEqual(len(field_values_page), 2)

        # Each item should have type, id, and dynamic attributes
        for item_fields in field_values_page:
            field_names = [fv[0] for fv in item_fields]
            self.assertIn("type", field_names)
            self.assertIn("id", field_names)
            self.assertIn("amount", field_names)
            self.assertIn("cost", field_names)
            self.assertIn("net", field_names)
            self.assertIn("hours", field_names)
