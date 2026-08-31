"""Tests for invoice user rates functionality."""

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

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
        """Test that invoice cost reflects each time entry's user rate.

        Time entries don't persist a per-entry cost field; the user-rate
        based cost is only accumulated onto the parent Invoice (see
        db/signals.py: update_invoice_on_time_save). Amount, meanwhile, is
        calculated from the task's rate, not the user's.
        """
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

        for invoice in Invoice.objects.all():
            expected_cost = sum(
                (time_entry.user.rate * time_entry.hours)
                for time_entry in invoice.times.all()
                if time_entry.user and time_entry.user.rate
            )
            self.assertEqual(
                invoice.cost,
                expected_cost,
                f"Invoice {invoice.id}: expected cost {expected_cost} from "
                f"summed user rate * hours, got {invoice.cost}",
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
        response = self.client.get(reverse("invoice_view", args=[invoice.id]))
        
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

        # Each calculation should have the required fields including new ones
        for calc in user_calculations:
            self.assertIn("username", calc)
            self.assertIn("hours", calc)
            self.assertIn("user_rate", calc)
            self.assertIn("task_rate", calc)
            self.assertIn("amount", calc)
            self.assertIn("cost", calc)
            self.assertIn("difference", calc)

        # Check that totals are in the context including new ones
        self.assertIn("calc_total_hours", response.context)
        self.assertIn("calc_total_amount", response.context)
        self.assertIn("calc_total_cost", response.context)
        self.assertIn("calc_total_difference", response.context)

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
        response = self.client.get(reverse("invoice_view", args=[invoice.id]))

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

    def test_user_rate_calculations_show_task_and_user_rates(self):
        """Test that user calculations show both task rates and user rates with difference."""
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

        # Login and get the page
        superuser = SiteUser.objects.create_superuser(
            username="testadmin", 
            password="testpass"
        )
        self.client.force_login(superuser)
        response = self.client.get(reverse("invoice_view", args=[invoice.id]))

        # Get user calculations from context
        user_calculations = response.context["user_calculations"]
        
        # Verify each user calculation has the new fields
        for calc in user_calculations:
            # Should have task_rate (average billing rate)
            self.assertIn("task_rate", calc)
            
            # Should have user_rate (cost rate)
            self.assertIn("user_rate", calc)
            
            # Should have cost (user_rate * hours)
            self.assertIn("cost", calc)
            
            # Should have difference (amount - cost)
            self.assertIn("difference", calc)
            
            # If user has a rate, verify cost calculation
            if calc["user_rate"] is not None:
                expected_cost = calc["user_rate"] * calc["hours"]
                self.assertEqual(
                    calc["cost"],
                    expected_cost,
                    f"User {calc['username']}: expected cost {expected_cost}, got {calc['cost']}"
                )
            
            # Verify difference calculation
            expected_difference = calc["amount"] - calc["cost"]
            self.assertEqual(
                calc["difference"],
                expected_difference,
                f"User {calc['username']}: expected difference {expected_difference}, got {calc['difference']}"
            )
        
        # Verify total calculations
        calc_total_cost = response.context["calc_total_cost"]
        calc_total_difference = response.context["calc_total_difference"]
        calc_total_amount = response.context["calc_total_amount"]
        
        # Total difference should equal total amount - total cost
        expected_total_difference = calc_total_amount - calc_total_cost
        self.assertEqual(
            calc_total_difference,
            expected_total_difference,
            f"Expected total difference {expected_total_difference}, got {calc_total_difference}"
        )
