"""Integration tests for Invoice creation with start_date and end_date fields."""

from datetime import date
from django.test import TestCase
from db.models import Invoice, Project, Company, Client
from siteuser.models import SiteUser


class InvoiceModelFieldTests(TestCase):
    """Test that Invoice model has required fields for form submission."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a user
        self.user = SiteUser.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Create company, client, and project hierarchy
        self.company = Company.objects.create(name='Test Company')
        self.client = Client.objects.create(name='Test Client', company=self.company)
        self.project = Project.objects.create(name='Test Project', client=self.client)
    
    def test_invoice_has_start_date_and_end_date_fields(self):
        """Test that Invoice model has start_date and end_date fields."""
        # This should not raise an error
        invoice = Invoice.objects.create(
            name='Test Invoice',
            project=self.project,
            issue_date=date(2026, 1, 15),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 31),
            due_date=date(2026, 2, 15),
            paid_amount=0
        )
        
        # Verify the fields were saved correctly
        self.assertEqual(invoice.start_date, date(2026, 1, 1))
        self.assertEqual(invoice.end_date, date(2026, 1, 31))
        
        # Verify we can retrieve the invoice with these fields
        retrieved = Invoice.objects.get(pk=invoice.pk)
        self.assertEqual(retrieved.start_date, date(2026, 1, 1))
        self.assertEqual(retrieved.end_date, date(2026, 1, 31))
    
    def test_invoice_date_fields_can_be_null(self):
        """Test that Invoice start_date and end_date can be null."""
        # This should not raise an error
        invoice = Invoice.objects.create(
            name='Test Invoice Without Dates',
            project=self.project,
            issue_date=date(2026, 1, 15),
            start_date=None,
            end_date=None,
            due_date=date(2026, 2, 15),
            paid_amount=0
        )
        
        # Verify the fields are null
        self.assertIsNone(invoice.start_date)
        self.assertIsNone(invoice.end_date)
    
    def test_invoice_form_fields_match_model_fields(self):
        """Test that all fields in InvoiceForm exist on Invoice model."""
        from db.forms import InvoiceForm
        
        form_fields = InvoiceForm.Meta.fields
        invoice = Invoice()
        
        # Verify each form field exists on the model
        for field_name in form_fields:
            self.assertTrue(
                hasattr(invoice, field_name),
                f"Invoice model is missing field '{field_name}' declared in InvoiceForm"
            )
