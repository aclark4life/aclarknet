"""Tests for Invoice view redirect behavior."""

from unittest.mock import MagicMock, Mock, patch

from django.test import RequestFactory, TestCase
from django.urls import reverse

from db.models import Invoice, Project
from db.views.invoice import InvoiceCreateView, InvoiceUpdateView
from siteuser.models import SiteUser


class InvoiceViewRedirectTests(TestCase):
    """Test that invoice views redirect properly after save."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.user = Mock(spec=SiteUser)
        self.user.is_superuser = True
        self.user.is_authenticated = True

    @patch('db.views.invoice.Project.objects.get')
    def test_invoice_create_view_form_valid_with_project_id(self, mock_project_get):
        """Test that InvoiceCreateView sets project and redirects correctly."""
        # Create a mock project
        mock_project = Mock(spec=Project)
        mock_project.pk = 'project123'
        mock_project_get.return_value = mock_project
        
        # Create a mock form with an instance
        mock_form = Mock()
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.pk = 'invoice123'
        mock_form.instance = mock_invoice
        mock_form.save.return_value = mock_invoice
        
        # Create the view
        view = InvoiceCreateView()
        request = self.factory.post('/invoice/create/?project_id=project123')
        request.user = self.user
        view.request = request
        
        # Mock get_success_url to avoid URL resolution issues
        view.get_success_url = Mock(return_value='/invoice/invoice123/')
        
        # Call form_valid
        response = view.form_valid(mock_form)
        
        # Verify that the project was set on the form instance
        self.assertEqual(mock_form.instance.project, mock_project)
        
        # Verify that form.save() was called by the parent
        self.assertTrue(mock_form.save.called)
        
        # Verify that we got a redirect response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/invoice/invoice123/')

    def test_invoice_create_view_form_valid_without_project_id(self):
        """Test that InvoiceCreateView works without project_id."""
        # Create a mock form with an instance
        mock_form = Mock()
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.pk = 'invoice456'
        mock_form.instance = mock_invoice
        mock_form.save.return_value = mock_invoice
        
        # Create the view
        view = InvoiceCreateView()
        request = self.factory.post('/invoice/create/')
        request.user = self.user
        view.request = request
        
        # Mock get_success_url to avoid URL resolution issues
        view.get_success_url = Mock(return_value='/invoice/invoice456/')
        
        # Call form_valid
        response = view.form_valid(mock_form)
        
        # Verify that form.save() was called by the parent
        self.assertTrue(mock_form.save.called)
        
        # Verify that we got a redirect response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/invoice/invoice456/')

    def test_invoice_update_view_form_valid(self):
        """Test that InvoiceUpdateView redirects correctly.

        InvoiceUpdateView.form_valid() builds a TimeEntryFormSet keyed off
        self.object, which requires a real model instance (Django's
        relation-field checks inspect ._meta.model on the instance). A bare
        Mock(spec=Invoice) doesn't provide usable metadata for that, so we
        use a real, saved Invoice instead.
        """
        real_invoice = Invoice.objects.create(name="Invoice 789")

        # Create a mock form with a real instance
        mock_form = Mock()
        mock_form.instance = real_invoice
        mock_form.save.return_value = real_invoice
        
        # Create the view
        view = InvoiceUpdateView()
        # Include valid (empty) time formset management data so
        # get_time_formset().is_valid() succeeds and form_valid() takes
        # the redirect path being tested here.
        post_data = {
            "times-TOTAL_FORMS": "0",
            "times-INITIAL_FORMS": "0",
            "times-MIN_NUM_FORMS": "0",
            "times-MAX_NUM_FORMS": "1000",
        }
        request = self.factory.post(
            f'/invoice/{real_invoice.pk}/update/', post_data
        )
        request.user = self.user
        view.request = request
        view.kwargs = {"pk": real_invoice.pk}
        view.object = real_invoice  # UpdateView has object set
        
        # Mock get_success_url to avoid URL resolution issues
        view.get_success_url = Mock(return_value=f'/invoice/{real_invoice.pk}/')
        
        # Call form_valid
        response = view.form_valid(mock_form)
        
        # Verify that form.save() was called by the parent
        self.assertTrue(mock_form.save.called)
        
        # Verify that we got a redirect response
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/invoice/{real_invoice.pk}/')

    def test_invoice_create_view_no_double_save(self):
        """Test that the invoice is not saved multiple times."""
        # Create a mock form with an instance
        mock_form = Mock()
        mock_invoice = Mock(spec=Invoice)
        mock_invoice.pk = 'invoice999'
        mock_form.instance = mock_invoice
        mock_form.save.return_value = mock_invoice
        
        # Create the view
        view = InvoiceCreateView()
        request = self.factory.post('/invoice/create/')
        request.user = self.user
        view.request = request
        
        # Mock get_success_url to avoid URL resolution issues
        view.get_success_url = Mock(return_value='/invoice/invoice999/')
        
        # Call form_valid
        response = view.form_valid(mock_form)
        
        # Verify that form.save() was called exactly once (by the parent's form_valid)
        self.assertEqual(mock_form.save.call_count, 1)


class InvoiceDeleteViewTests(TestCase):
    """Test that InvoiceDeleteView actually deletes invoices.

    Regression test for a bug where InvoiceDeleteView inherited
    form_class = InvoiceForm from BaseInvoiceView. DeleteView's POST
    handler validates that form against the (empty) confirmation POST
    body, so required InvoiceForm fields (issue_date, paid_amount,
    currency) failed validation and the invoice was silently never
    deleted -- the confirmation page just re-rendered with a 200.
    """

    def setUp(self):
        self.superuser = SiteUser.objects.create_superuser(
            username="admin-delete-test", password="password123"
        )
        self.client.force_login(self.superuser)

    def test_post_deletes_invoice_and_redirects(self):
        invoice = Invoice.objects.create(name="Invoice To Delete")
        url = reverse("invoice_delete", args=[invoice.pk])

        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Invoice.objects.filter(pk=invoice.pk).exists())

    def test_get_renders_confirmation_page(self):
        invoice = Invoice.objects.create(name="Invoice To Confirm Delete")
        url = reverse("invoice_delete", args=[invoice.pk])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Invoice.objects.filter(pk=invoice.pk).exists())
