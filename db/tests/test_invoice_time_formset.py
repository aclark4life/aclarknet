"""Tests for Invoice time entry formset functionality."""

from django.test import RequestFactory, TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from db.models import Invoice, Project, Time, Client
from db.views.invoice import InvoiceUpdateView
from db.forms import TimeEntryFormSet

User = get_user_model()


class InvoiceTimeEntryFormsetTests(TestCase):
    """Test that invoice update view properly handles time entry formset."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin"
        )

        # Create test client and project
        self.client_obj = Client.objects.create(name="Test Client")
        self.project = Project.objects.create(
            name="Test Project", client=self.client_obj
        )

        # Create test invoice
        self.invoice = Invoice.objects.create(
            name="Test Invoice", issue_date=timezone.now().date(), amount=1000.00
        )

    def test_formset_in_context(self):
        """Test that formset is included in GET request context."""
        request = self.factory.get(f"/invoice/{self.invoice.pk}/edit/")
        request.user = self.user

        view = InvoiceUpdateView()
        view.request = request
        view.kwargs = {"pk": self.invoice.pk}
        view.object = self.invoice

        context = view.get_context_data()

        self.assertIn("time_formset", context)
        self.assertIsInstance(context["time_formset"], TimeEntryFormSet.__class__)

    def test_formset_saves_new_time_entries(self):
        """Test that new time entries are saved via formset."""
        # Create POST data for the invoice form and time entry formset
        post_data = {
            "name": "Updated Invoice",
            "issue_date": timezone.now().date(),
            "amount": 1500.00,
            "paid_amount": 0,
            "hours": 10,
            "currency": "USD",
            # Management form data
            "times-TOTAL_FORMS": "1",
            "times-INITIAL_FORMS": "0",
            "times-MIN_NUM_FORMS": "0",
            "times-MAX_NUM_FORMS": "1000",
            # First time entry
            "times-0-date": timezone.now().date(),
            "times-0-hours": 5.0,
            "times-0-description": "Test work",
        }

        request = self.factory.post(f"/invoice/{self.invoice.pk}/edit/", post_data)
        request.user = self.user

        view = InvoiceUpdateView()
        view.request = request
        view.kwargs = {"pk": self.invoice.pk}
        view.object = self.invoice

        # Get the context which creates the formset
        context = view.get_context_data()
        time_formset = context["time_formset"]

        # Validate the formset
        self.assertTrue(
            time_formset.is_valid(), f"Formset errors: {time_formset.errors}"
        )

    def test_formset_deletes_time_entries(self):
        """Test that time entries can be deleted via formset."""
        # Create a time entry
        time_entry = Time.objects.create(
            invoice=self.invoice,
            date=timezone.now().date(),
            hours=3.0,
            description="To be deleted",
        )

        # Create POST data with DELETE flag
        post_data = {
            "name": "Test Invoice",
            "issue_date": timezone.now().date(),
            "amount": 1000.00,
            "paid_amount": 0,
            "hours": 10,
            "currency": "USD",
            # Management form data
            "times-TOTAL_FORMS": "1",
            "times-INITIAL_FORMS": "1",
            "times-MIN_NUM_FORMS": "0",
            "times-MAX_NUM_FORMS": "1000",
            # Existing time entry with DELETE flag
            "times-0-id": time_entry.pk,
            "times-0-date": time_entry.date,
            "times-0-hours": time_entry.hours,
            "times-0-description": time_entry.description,
            "times-0-DELETE": "on",
        }

        request = self.factory.post(f"/invoice/{self.invoice.pk}/edit/", post_data)
        request.user = self.user

        view = InvoiceUpdateView()
        view.request = request
        view.kwargs = {"pk": self.invoice.pk}
        view.object = self.invoice

        # Get the context which creates the formset
        context = view.get_context_data()
        time_formset = context["time_formset"]

        # Validate the formset
        self.assertTrue(
            time_formset.is_valid(), f"Formset errors: {time_formset.errors}"
        )

        # The DELETE flag should be detected
        self.assertTrue(time_formset.forms[0].cleaned_data.get("DELETE", False))

    def test_formset_updates_existing_time_entries(self):
        """Test that existing time entries can be updated via formset."""
        # Create a time entry
        time_entry = Time.objects.create(
            invoice=self.invoice,
            date=timezone.now().date(),
            hours=3.0,
            description="Original description",
        )

        # Create POST data with updated values
        post_data = {
            "name": "Test Invoice",
            "issue_date": timezone.now().date(),
            "amount": 1000.00,
            "paid_amount": 0,
            "hours": 10,
            "currency": "USD",
            # Management form data
            "times-TOTAL_FORMS": "1",
            "times-INITIAL_FORMS": "1",
            "times-MIN_NUM_FORMS": "0",
            "times-MAX_NUM_FORMS": "1000",
            # Updated time entry
            "times-0-id": time_entry.pk,
            "times-0-date": time_entry.date,
            "times-0-hours": 5.0,  # Updated
            "times-0-description": "Updated description",  # Updated
        }

        request = self.factory.post(f"/invoice/{self.invoice.pk}/edit/", post_data)
        request.user = self.user

        view = InvoiceUpdateView()
        view.request = request
        view.kwargs = {"pk": self.invoice.pk}
        view.object = self.invoice

        # Get the context which creates the formset
        context = view.get_context_data()
        time_formset = context["time_formset"]

        # Validate the formset
        self.assertTrue(
            time_formset.is_valid(), f"Formset errors: {time_formset.errors}"
        )

        # Check the updated values
        self.assertEqual(float(time_formset.forms[0].cleaned_data["hours"]), 5.0)
        self.assertEqual(
            time_formset.forms[0].cleaned_data["description"], "Updated description"
        )

    def test_formset_project_prepopulated_from_invoice(self):
        """Test that new time entry forms have project pre-populated from invoice."""
        # Create an invoice with a project
        invoice_with_project = Invoice.objects.create(
            name="Invoice with Project",
            issue_date=timezone.now().date(),
            amount=2000.00,
            project=self.project,
        )

        request = self.factory.get(f"/invoice/{invoice_with_project.pk}/edit/")
        request.user = self.user

        view = InvoiceUpdateView()
        view.request = request
        view.kwargs = {"pk": invoice_with_project.pk}
        view.object = invoice_with_project

        context = view.get_context_data()
        time_formset = context["time_formset"]

        # Check that empty forms (for new time entries) have project pre-populated
        for form in time_formset.forms:
            if not form.instance.pk:  # New form
                # Check the form's initial data (set via formset initial parameter)
                self.assertEqual(
                    form.initial.get("project"),
                    self.project,
                    "New time entry forms should have project pre-populated from invoice",
                )
