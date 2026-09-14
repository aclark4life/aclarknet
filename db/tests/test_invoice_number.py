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

    def test_invoice_name_auto_generated(self):
        """Test that name is auto-generated as '<project> <month> <year>'."""
        issue_date = timezone.now().date()
        invoice = Invoice.objects.create(
            issue_date=issue_date,
        )

        # Name should default to "<project> <month year>" (project falls back
        # to "Invoice" when no project is set).
        self.assertEqual(invoice.name, f"Invoice {issue_date.strftime('%B %Y')}")

    def test_invoice_name_uses_project(self):
        """Test that the auto-generated name includes the project name."""
        from db.models import Project

        project = Project.objects.create(name="Acme Corp")
        issue_date = timezone.now().date()
        invoice = Invoice.objects.create(
            project=project,
            issue_date=issue_date,
        )

        self.assertEqual(
            invoice.name, f"Acme Corp {issue_date.strftime('%B %Y')}"
        )
