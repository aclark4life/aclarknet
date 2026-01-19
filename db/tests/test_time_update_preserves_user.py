"""Test that updating a time entry preserves the user field."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from db.models import Time

User = get_user_model()


class TimeUpdatePreservesUserTest(TestCase):
    """Test that updating a time entry preserves the original user."""

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

    def test_update_preserves_user_field(self):
        """Test that updating a time entry doesn't lose the user."""
        # Create a time entry for the user
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Original work"
        )
        original_id = time_entry.pk
        print(f"Created time entry: user={time_entry.user.username}, id={original_id}")
        
        # Update the time entry through the form (not including user in POST data)
        response = self.client.post(f'/dashboard/time/{time_entry.pk}/update/', {
            'date': '2024-01-15',
            'hours': '10.0',
            'description': 'Updated work'
        })
        print(f"Update response status: {response.status_code}")
        
        # Refresh from database
        time_entry.refresh_from_db()
        print(f"After update: user={time_entry.user}, hours={time_entry.hours}, desc={time_entry.description}")
        
        # Verify the user field is still set
        self.assertIsNotNone(time_entry.user, "User field should not be None after update")
        self.assertEqual(time_entry.user, self.user, "User should still be the original user after update")
        self.assertEqual(time_entry.hours, 10.0)
        self.assertEqual(time_entry.description, 'Updated work')
    
    def test_update_form_includes_user_field(self):
        """Test that the update form includes the user field (as hidden)."""
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Original work"
        )
        
        # Get the update form
        response = self.client.get(f'/dashboard/time/{time_entry.pk}/update/')
        self.assertEqual(response.status_code, 200)
        
        # Check if the user field is in the form (should be hidden)
        form_html = response.content.decode()
        print(f"User field in form: {'name=\"user\"' in form_html}")
        print(f"User ID in form: {str(self.user.pk) in form_html}")
        
        # The form should include the user field
        self.assertIn('name="user"', form_html, "User field should be in the form")
