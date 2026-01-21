"""Tests for invoice number functionality."""

from django.test import TestCase
from django.utils import timezone

from db.models import Invoice


class InvoiceNumberTest(TestCase):
    """Test invoice number generation."""

    def test_invoice_number_auto_generated(self):
        """Test that invoice numbers are automatically generated."""
        invoice1 = Invoice.objects.create(
            name="Test Invoice 1",
            issue_date=timezone.now().date(),
        )
        
        self.assertIsNotNone(invoice1.invoice_number)
        self.assertIsInstance(invoice1.invoice_number, int)
        self.assertEqual(invoice1.invoice_number, 1)

    def test_invoice_number_increments(self):
        """Test that invoice numbers increment."""
        invoice1 = Invoice.objects.create(
            name="Test Invoice 1",
            issue_date=timezone.now().date(),
        )
        invoice2 = Invoice.objects.create(
            name="Test Invoice 2",
            issue_date=timezone.now().date(),
        )
        
        self.assertEqual(invoice1.invoice_number, 1)
        self.assertEqual(invoice2.invoice_number, 2)

    def test_invoice_number_unique(self):
        """Test that invoice numbers are unique."""
        invoice1 = Invoice.objects.create(
            name="Test Invoice 1",
            issue_date=timezone.now().date(),
        )
        
        # Create invoice with same number should fail
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Invoice.objects.create(
                name="Test Invoice 2",
                invoice_number=invoice1.invoice_number,
                issue_date=timezone.now().date(),
            )

    def test_invoice_number_in_name(self):
        """Test that invoice number is included in auto-generated name."""
        invoice = Invoice.objects.create(
            issue_date=timezone.now().date(),
        )
        
        # Name should be auto-generated with invoice_number
        self.assertIn(str(invoice.invoice_number), invoice.name)
