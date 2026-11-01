"""Tests for Dashboard view filtering."""

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from db.models import Time
from db.views.dashboard import DashboardView

User = get_user_model()


class DashboardViewTest(TestCase):
    """Test that Dashboard view filters time entries by user."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpass123",
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpass123",
        )
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

        # Create time entries for both users
        self.time1_user1 = Time.objects.create(
            user=self.user1,
            hours=8.0,
            description="User1 work entry 1",
        )
        self.time2_user1 = Time.objects.create(
            user=self.user1,
            hours=4.0,
            description="User1 work entry 2",
        )
        self.time1_user2 = Time.objects.create(
            user=self.user2,
            hours=6.0,
            description="User2 work entry 1",
        )

    def test_dashboard_shows_only_session_user_times(self):
        """Test that dashboard shows only time entries for the logged-in user."""
        # Create a request as user1
        request = self.factory.get('/dashboard/')
        request.user = self.user1

        # Create the view and get context
        view = DashboardView()
        view.request = request
        view.object_list = []
        context = view.get_context_data()

        # Get the times queryset from context
        times = context['times']

        # Verify only user1's time entries are in the queryset
        self.assertEqual(times.count(), 2)
        self.assertIn(self.time1_user1, times)
        self.assertIn(self.time2_user1, times)
        self.assertNotIn(self.time1_user2, times)

    def test_dashboard_shows_only_session_user_times_for_user2(self):
        """Test that dashboard shows only time entries for user2 when logged in as user2."""
        # Create a request as user2
        request = self.factory.get('/dashboard/')
        request.user = self.user2

        # Create the view and get context
        view = DashboardView()
        view.request = request
        view.object_list = []
        context = view.get_context_data()

        # Get the times queryset from context
        times = context['times']

        # Verify only user2's time entry is in the queryset
        self.assertEqual(times.count(), 1)
        self.assertIn(self.time1_user2, times)
        self.assertNotIn(self.time1_user1, times)
        self.assertNotIn(self.time2_user1, times)

    def test_dashboard_superuser_sees_all_times(self):
        """Test that superuser sees all time entries in the dashboard."""
        # Create a request as superuser
        request = self.factory.get('/dashboard/')
        request.user = self.superuser

        # Create the view and get context
        view = DashboardView()
        view.request = request
        view.object_list = []
        context = view.get_context_data()

        # Get the times queryset from context
        times = context['times']

        # Verify all time entries are in the queryset for superuser
        self.assertEqual(times.count(), 3)
        self.assertIn(self.time1_user1, times)
        self.assertIn(self.time2_user1, times)
        self.assertIn(self.time1_user2, times)

    def test_dashboard_time_stats_calculated_for_session_user_only(self):
        """Test that time statistics are calculated only from session user's entries."""
        # Create a request as user1
        request = self.factory.get('/dashboard/')
        request.user = self.user1

        # Create the view and get context
        view = DashboardView()
        view.request = request
        view.object_list = []
        context = view.get_context_data()

        # Get time statistics
        statcard = context['statcard']['times']
        entered = statcard['entered']

        # Verify the entered hours are only from user1 (8.0 + 4.0 = 12.0)
        self.assertEqual(entered, 12.0)


class DashboardMonthlyStatcardsTest(TestCase):
    """Test that Dashboard view reports unpaid-since-last-month totals
    alongside cumulative totals."""

    def setUp(self):
        from datetime import date
        from decimal import Decimal

        from django.utils import timezone

        from db.models import Invoice

        self.factory = RequestFactory()
        self.superuser = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        today = timezone.localdate()

        def invoice(name, issue_date, amount, cost, paid):
            # Set totals with update() so the post_save signal, which
            # recomputes them from time entries, doesn't zero them out.
            obj = Invoice.objects.create(name=name, issue_date=issue_date)
            Invoice.objects.filter(pk=obj.pk).update(
                amount=Decimal(amount),
                cost=Decimal(cost),
                net=Decimal(amount) - Decimal(cost),
                paid_amount=Decimal(paid),
                balance=Decimal(amount) - Decimal(paid),
            )

        invoice("Unpaid this month", today, "1000", "400", "0")
        invoice("Paid this month", today, "300", "100", "300")
        invoice(
            "Unpaid last year", date(today.year - 1, today.month, 1), "500", "100", "0"
        )

    def get_statcards(self):
        request = self.factory.get("/dashboard/")
        request.user = self.superuser
        view = DashboardView()
        view.request = request
        view.object_list = []
        return view.get_context_data()["statcards"]

    def test_monthly_and_cumulative_totals(self):
        statcards = self.get_statcards()
        self.assertEqual(
            statcards["dashboard"]["invoices"],
            {"gross": 1800, "cost": 600, "net": 1200},
        )
        self.assertEqual(
            statcards["monthly"]["invoices"],
            {"gross": 1000, "cost": 400, "net": 600},
        )
        self.assertTrue(statcards["monthly"]["label"].startswith("Unpaid since"))

    def test_cumulative_sparkline_trend(self):
        import json

        statcards = self.get_statcards()
        self.assertNotIn("sparklines", statcards["monthly"])

        # Last year's invoice falls just outside the 12-month window, so it
        # only contributes to the running total's starting point.
        gross = json.loads(statcards["dashboard"]["sparklines"]["gross"])[0]
        self.assertEqual(len(gross), 12)
        self.assertEqual(gross[0], 500)
        self.assertEqual(gross[-1], 1800)
