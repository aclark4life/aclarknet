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
