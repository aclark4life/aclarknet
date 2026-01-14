"""Tests for invoice user rates functionality."""

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from db.models import Invoice, Time
from siteuser.models import SiteUser


class InvoiceUserRatesTest(TestCase):
    """Test that invoices show user-based rate calculations."""

    def test_users_created_with_different_rates(self):
        """Test that users are created with different rates."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=1",
            "--invoices=1",
            "--times=1",
            "--users=10",
            stdout=StringIO(),
        )

        # Check that users have different rates
        users = SiteUser.objects.all()
        rates = set()
        for user in users:
            if user.rate:
                rates.add(user.rate)
        
        # Should have multiple different rates (at least 2)
        self.assertGreaterEqual(
            len(rates), 
            2, 
            f"Expected multiple different rates, got {rates}"
        )

    def test_time_amount_uses_user_rate(self):
        """Test that time entry amounts use user rates when available."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=1",
            "--invoices=1",
            "--times=5",
            "--users=3",
            stdout=StringIO(),
        )

        # Check that time entries use user rates for calculation
        time_entries = Time.objects.all()
        for time_entry in time_entries:
            if time_entry.user and time_entry.user.rate:
                # Amount should be user.rate * hours
                expected_amount = time_entry.user.rate * time_entry.hours
                self.assertEqual(
                    time_entry.amount,
                    expected_amount,
                    f"Time entry {time_entry.id}: expected {expected_amount} "
                    f"(user rate {time_entry.user.rate} * {time_entry.hours} hours), "
                    f"got {time_entry.amount}",
                )

    def test_invoice_detail_view_includes_user_calculations(self):
        """Test that invoice detail view includes user rate calculations."""
        # Create test data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=1",
            "--invoices=1",
            "--times=10",
            "--users=3",
            stdout=StringIO(),
        )

        # Get an invoice
        invoice = Invoice.objects.first()
        self.assertIsNotNone(invoice, "Should have at least one invoice")

        # Login as superuser to access invoice detail view
        superuser = SiteUser.objects.create_superuser(
            username="testadmin", 
            password="testpass"
        )
        self.client.force_login(superuser)

        # Get the invoice detail page
        response = self.client.get(f"/invoice/{invoice.id}/")
        
        # Check response is successful
        self.assertEqual(response.status_code, 200)

        # Check that user_calculations is in the context
        self.assertIn("user_calculations", response.context)
        user_calculations = response.context["user_calculations"]

        # Should have at least one user's calculations
        self.assertGreater(
            len(user_calculations), 
            0, 
            "Should have user calculations in context"
        )

        # Each calculation should have the required fields
        for calc in user_calculations:
            self.assertIn("username", calc)
            self.assertIn("hours", calc)
            self.assertIn("rate", calc)
            self.assertIn("amount", calc)

        # Check that totals are in the context
        self.assertIn("calc_total_hours", response.context)
        self.assertIn("calc_total_amount", response.context)

    def test_user_calculations_sum_correctly(self):
        """Test that user calculations sum to invoice total."""
        # Create test data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=1",
            "--invoices=1",
            "--times=15",
            "--users=5",
            stdout=StringIO(),
        )

        # Get an invoice
        invoice = Invoice.objects.first()
        
        # Calculate expected totals from time entries
        times = Time.objects.filter(invoice=invoice)
        expected_hours = sum(t.hours or Decimal('0') for t in times)
        expected_amount = sum(t.amount or Decimal('0') for t in times)

        # Login and get the page
        superuser = SiteUser.objects.create_superuser(
            username="testadmin", 
            password="testpass"
        )
        self.client.force_login(superuser)
        response = self.client.get(f"/invoice/{invoice.id}/")

        # Check that calculated totals match
        calc_total_hours = response.context["calc_total_hours"]
        calc_total_amount = response.context["calc_total_amount"]

        self.assertEqual(
            calc_total_hours,
            expected_hours,
            f"Total hours mismatch: expected {expected_hours}, got {calc_total_hours}",
        )
        self.assertEqual(
            calc_total_amount,
            expected_amount,
            f"Total amount mismatch: expected {expected_amount}, got {calc_total_amount}",
        )
