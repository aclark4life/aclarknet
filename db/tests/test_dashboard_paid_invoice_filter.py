"""Tests for Dashboard view filtering of paid invoice time entries."""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from db.models import Invoice, Time
from db.views.dashboard import DashboardView

User = get_user_model()


class DashboardPaidInvoiceFilterTest(TestCase):
    """Test that Dashboard view excludes time entries from paid invoices."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        # Create an unpaid invoice
        self.unpaid_invoice = Invoice.objects.create(
            name="Unpaid Invoice",
            amount=Decimal("1000.00"),
            paid_amount=Decimal("0.00"),
            balance=Decimal("1000.00"),
        )

        # Create a partially paid invoice
        self.partially_paid_invoice = Invoice.objects.create(
            name="Partially Paid Invoice",
            amount=Decimal("1000.00"),
            paid_amount=Decimal("500.00"),
            balance=Decimal("500.00"),
        )

        # Create a fully paid invoice (balance = 0)
        self.paid_invoice = Invoice.objects.create(
            name="Paid Invoice",
            amount=Decimal("1000.00"),
            paid_amount=Decimal("1000.00"),
            balance=Decimal("0.00"),
        )

        # Create time entries for each invoice
        self.time_no_invoice = Time.objects.create(
            user=self.user,
            hours=Decimal("2.0"),
            description="Time with no invoice",
            invoice=None,
        )

        self.time_unpaid_invoice = Time.objects.create(
            user=self.user,
            hours=Decimal("3.0"),
            description="Time with unpaid invoice",
            invoice=self.unpaid_invoice,
        )

        self.time_partially_paid_invoice = Time.objects.create(
            user=self.user,
            hours=Decimal("4.0"),
            description="Time with partially paid invoice",
            invoice=self.partially_paid_invoice,
        )

        self.time_paid_invoice = Time.objects.create(
            user=self.user,
            hours=Decimal("5.0"),
            description="Time with paid invoice",
            invoice=self.paid_invoice,
        )

    def test_dashboard_excludes_paid_invoice_times(self):
        """Test that dashboard excludes time entries associated with paid invoices."""
        request = self.factory.get('/dashboard/')
        request.user = self.user

        view = DashboardView()
        view.request = request
        view.object_list = []
        context = view.get_context_data()

        times = context['times']

        # Should include time entries with no invoice
        self.assertIn(self.time_no_invoice, times)

        # Should include time entries with unpaid invoices
        self.assertIn(self.time_unpaid_invoice, times)

        # Should include time entries with partially paid invoices
        self.assertIn(self.time_partially_paid_invoice, times)

        # Should NOT include time entries with fully paid invoices
        self.assertNotIn(self.time_paid_invoice, times)

    def test_dashboard_time_count_excludes_paid_invoice_times(self):
        """Test that the time count in dashboard excludes paid invoice times."""
        request = self.factory.get('/dashboard/')
        request.user = self.user

        view = DashboardView()
        view.request = request
        view.object_list = []
        context = view.get_context_data()

        times = context['times']

        # Should have 3 time entries (no invoice, unpaid, partially paid)
        # Should NOT include the paid invoice time entry
        self.assertEqual(times.count(), 3)

    def test_dashboard_stats_exclude_paid_invoice_hours(self):
        """Test that dashboard statistics exclude hours from paid invoices."""
        request = self.factory.get('/dashboard/')
        request.user = self.user

        view = DashboardView()
        view.request = request
        view.object_list = []
        context = view.get_context_data()

        statcard = context['statcard']['times']
        entered = statcard['entered']

        # Should sum: 2.0 (no invoice) + 3.0 (unpaid) + 4.0 (partially paid) = 9.0
        # Should NOT include: 5.0 (paid invoice)
        self.assertEqual(entered, Decimal("9.0"))
