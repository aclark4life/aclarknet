"""Tests for Time view permission checks."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from db.models import Time

User = get_user_model()


class TimeViewPermissionTest(TestCase):
    """Test that Time views handle permissions correctly."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create two regular users
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

        # Create a superuser
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

        # Create time entries for each user
        self.time1 = Time.objects.create(
            user=self.user1, hours=8.0, description="User 1 work"
        )
        self.time2 = Time.objects.create(
            user=self.user2, hours=6.0, description="User 2 work"
        )

    def test_time_detail_view_owner_can_access(self):
        """Test that a user can view their own time entry."""
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(f"/dashboard/time/{self.time1.pk}/")

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

    def test_time_detail_view_non_owner_forbidden(self):
        """Test that a user cannot view another user's time entry."""
        self.client.login(username="user2", password="testpass123")
        response = self.client.get(f"/dashboard/time/{self.time1.pk}/")

        # Should return 403 Forbidden, not 500 Internal Server Error
        self.assertEqual(response.status_code, 403)

    def test_time_detail_view_admin_can_access_all(self):
        """Test that admin can view any time entry."""
        self.client.login(username="admin", password="adminpass123")

        response1 = self.client.get(f"/dashboard/time/{self.time1.pk}/")
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(f"/dashboard/time/{self.time2.pk}/")
        self.assertEqual(response2.status_code, 200)

    def test_time_update_view_owner_can_access(self):
        """Test that a user can update their own time entry."""
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(f"/dashboard/time/{self.time1.pk}/update/")

        # Should return 200 OK
        self.assertEqual(response.status_code, 200)

    def test_time_update_view_non_owner_forbidden(self):
        """Test that a user cannot update another user's time entry."""
        self.client.login(username="user2", password="testpass123")
        response = self.client.get(f"/dashboard/time/{self.time1.pk}/update/")

        # Should return 403 Forbidden, not 500 Internal Server Error
        self.assertEqual(response.status_code, 403)

    def test_time_delete_view_owner_can_access(self):
        """Test that a user can delete their own time entry."""
        self.client.login(username="user1", password="testpass123")
        response = self.client.get(f"/dashboard/time/{self.time1.pk}/delete/")

        # Should return 200 OK (shows delete confirmation page)
        self.assertEqual(response.status_code, 200)

    def test_time_delete_view_non_owner_forbidden(self):
        """Test that a user cannot delete another user's time entry."""
        self.client.login(username="user2", password="testpass123")
        response = self.client.get(f"/dashboard/time/{self.time1.pk}/delete/")

        # Should return 404 because FilterByUserMixin filters out objects not owned by the user
        # This is more secure than 403 as it doesn't reveal the existence of the object
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_redirected_to_login(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(f"/dashboard/time/{self.time1.pk}/")

        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_time_delete_view_owner_can_delete_post(self):
        """Test that a user can actually delete their own time entry via POST."""
        self.client.login(username="user1", password="testpass123")

        # Verify the time entry exists
        self.assertTrue(Time.objects.filter(pk=self.time1.pk).exists())

        # POST to delete the time entry
        response = self.client.post(f"/dashboard/time/{self.time1.pk}/delete/")

        # Should redirect to success URL (302)
        self.assertEqual(response.status_code, 302)

        # Verify the time entry was deleted
        self.assertFalse(Time.objects.filter(pk=self.time1.pk).exists())

    def test_time_delete_view_non_owner_cannot_delete_post(self):
        """Test that a user cannot delete another user's time entry via POST."""
        self.client.login(username="user2", password="testpass123")

        # Verify the time entry exists
        self.assertTrue(Time.objects.filter(pk=self.time1.pk).exists())

        # Try to POST to delete the time entry
        response = self.client.post(f"/dashboard/time/{self.time1.pk}/delete/")

        # Should return 404 (object not found in filtered queryset) or 403
        self.assertIn(response.status_code, [403, 404])

        # Verify the time entry was NOT deleted
        self.assertTrue(Time.objects.filter(pk=self.time1.pk).exists())
