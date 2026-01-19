"""Test to reproduce the issue where users cannot edit their own time entries."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from db.models import Time

User = get_user_model()


class UserCannotEditOwnTimeTest(TestCase):
    """Test that demonstrates the issue where users cannot edit their own time entries."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        # Create a regular user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
        )
        
        # Login as the user
        self.client.login(username="testuser", password="testpass123")

    def test_user_can_create_time_entry(self):
        """Test that a user can create a time entry."""
        response = self.client.post('/dashboard/time/create/', {
            'date': '2024-01-15',
            'hours': '8.0',
            'description': 'Test work'
        })
        
        # Should successfully create (redirect to success URL)
        self.assertIn(response.status_code, [200, 302])
        
        # Verify time entry was created
        time_entries = Time.objects.filter(description='Test work')
        self.assertEqual(time_entries.count(), 1)
        
        # Verify the user is assigned
        time_entry = time_entries.first()
        self.assertEqual(time_entry.user, self.user)
        print(f"Created time entry with user={time_entry.user}, id={time_entry.pk}")

    def test_user_can_edit_own_time_entry(self):
        """Test that a user can edit their own time entry."""
        # First, create a time entry for the user
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Original work"
        )
        print(f"Time entry: user={time_entry.user}, id={time_entry.pk}")
        
        # Try to access the edit form
        response = self.client.get(f'/dashboard/time/{time_entry.pk}/update/')
        print(f"GET update response status: {response.status_code}")
        
        # Should be able to access the edit form
        self.assertEqual(response.status_code, 200, 
                         f"User should be able to access their own time entry edit form. Got {response.status_code}")
        
        # Try to update the time entry
        response = self.client.post(f'/dashboard/time/{time_entry.pk}/update/', {
            'date': '2024-01-15',
            'hours': '10.0',
            'description': 'Updated work'
        })
        print(f"POST update response status: {response.status_code}")
        
        # Should successfully update (redirect)
        self.assertIn(response.status_code, [200, 302],
                     f"User should be able to update their own time entry. Got {response.status_code}")
        
        # Verify the time entry was updated
        time_entry.refresh_from_db()
        self.assertEqual(time_entry.hours, 10.0)
        self.assertEqual(time_entry.description, 'Updated work')
