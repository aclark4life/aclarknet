"""Test that admin users can still update time entries correctly."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from db.models import Time

User = get_user_model()


class AdminTimeUpdateTest(TestCase):
    """Test that admin users can update time entries without issues."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create a regular user
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="testpass123",
        )
        
        # Create an admin user
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )

    def test_admin_can_update_own_time_entry(self):
        """Test that admin can update their own time entry."""
        # Login as admin
        self.client.login(username="admin", password="adminpass123")
        
        # Create a time entry for admin
        time_entry = Time.objects.create(
            user=self.admin_user,
            hours=8.0,
            description="Admin work"
        )
        original_id = time_entry.pk
        print(f"Created time entry: user={time_entry.user.username}, id={original_id}")
        
        # Update the time entry
        response = self.client.post(f'/dashboard/time/{time_entry.pk}/update/', {
            'user': str(self.admin_user.pk),  # Admin form may include user field
            'date': '2024-01-15',
            'hours': '10.0',
            'description': 'Updated admin work',
            'task': '',  # Admin forms have these fields
            'invoice': '',
        })
        print(f"Update response status: {response.status_code}")
        
        # Refresh from database
        time_entry.refresh_from_db()
        print(f"After update: user={time_entry.user.username if time_entry.user else None}, hours={time_entry.hours}")
        
        # Verify the entry was updated correctly
        self.assertEqual(time_entry.user, self.admin_user)
        self.assertEqual(time_entry.hours, 10.0)
        self.assertEqual(time_entry.description, 'Updated admin work')

    def test_admin_can_update_other_users_time_entry(self):
        """Test that admin can update another user's time entry."""
        # Create a time entry for regular user
        time_entry = Time.objects.create(
            user=self.regular_user,
            hours=8.0,
            description="Regular user work"
        )
        original_user = time_entry.user
        print(f"Created time entry: user={time_entry.user.username}, id={time_entry.pk}")
        
        # Login as admin
        self.client.login(username="admin", password="adminpass123")
        
        # Admin updates the entry (but shouldn't change the user)
        response = self.client.post(f'/dashboard/time/{time_entry.pk}/update/', {
            'user': str(self.regular_user.pk),  # Keep original user
            'date': '2024-01-15',
            'hours': '12.0',
            'description': 'Updated by admin',
            'task': '',
            'invoice': '',
        })
        print(f"Update response status: {response.status_code}")
        
        # Refresh from database
        time_entry.refresh_from_db()
        print(f"After update: user={time_entry.user.username if time_entry.user else None}, hours={time_entry.hours}")
        
        # Verify the entry was updated correctly
        self.assertEqual(time_entry.user, original_user)
        self.assertEqual(time_entry.hours, 12.0)
        self.assertEqual(time_entry.description, 'Updated by admin')
