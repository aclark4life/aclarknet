"""End-to-end test for time entry creation and editing workflow."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from db.models import Time

User = get_user_model()


class TimeEntryWorkflowTest(TestCase):
    """Test the complete workflow of creating and editing time entries."""

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

    def test_complete_workflow_create_edit_own_entry(self):
        """Test that a user can create and then edit their own time entry."""
        # Login as user1
        self.client.login(username="user1", password="testpass123")
        
        # Step 1: Create a time entry
        response = self.client.post('/dashboard/time/create/', {
            'date': '2024-01-15',
            'hours': '8.0',
            'description': 'Initial work'
        })
        self.assertIn(response.status_code, [200, 302], "Should successfully create time entry")
        
        # Verify the time entry was created with correct user
        time_entry = Time.objects.filter(description='Initial work').first()
        self.assertIsNotNone(time_entry, "Time entry should be created")
        self.assertEqual(time_entry.user, self.user1, "Time entry should belong to user1")
        print(f"✓ Step 1: Created time entry for {time_entry.user.username}")
        
        # Step 2: Edit the time entry
        response = self.client.post(f'/dashboard/time/{time_entry.pk}/update/', {
            'date': '2024-01-16',
            'hours': '10.0',
            'description': 'Updated work'
        })
        self.assertIn(response.status_code, [200, 302], "Should successfully update time entry")
        
        # Verify the time entry was updated and user is preserved
        time_entry.refresh_from_db()
        self.assertEqual(time_entry.user, self.user1, "User should still be user1 after update")
        self.assertEqual(time_entry.hours, 10.0, "Hours should be updated")
        self.assertEqual(time_entry.description, 'Updated work', "Description should be updated")
        print(f"✓ Step 2: Updated time entry, user still {time_entry.user.username}")
        
        # Step 3: Edit again to verify it works multiple times
        response = self.client.post(f'/dashboard/time/{time_entry.pk}/update/', {
            'date': '2024-01-17',
            'hours': '12.0',
            'description': 'Final work'
        })
        self.assertIn(response.status_code, [200, 302], "Should successfully update time entry again")
        
        # Verify user is still preserved after multiple edits
        time_entry.refresh_from_db()
        self.assertEqual(time_entry.user, self.user1, "User should still be user1 after second update")
        self.assertEqual(time_entry.hours, 12.0, "Hours should be updated again")
        self.assertEqual(time_entry.description, 'Final work', "Description should be updated again")
        print(f"✓ Step 3: Updated again, user still {time_entry.user.username}")
        
        print("\n✅ Complete workflow test passed!")

    def test_user_cannot_edit_others_entry(self):
        """Test that a user cannot edit another user's time entry."""
        # Create a time entry for user1
        time_entry = Time.objects.create(
            user=self.user1,
            hours=8.0,
            description="User1's work"
        )
        
        # Login as user2
        self.client.login(username="user2", password="testpass123")
        
        # Try to access user1's time entry
        response = self.client.get(f'/dashboard/time/{time_entry.pk}/update/')
        self.assertEqual(response.status_code, 403, 
                        "User2 should not be able to access user1's time entry")
        print("✓ Permission check passed: user2 cannot access user1's entry")

    def test_multiple_users_independent_entries(self):
        """Test that multiple users can create and edit their own entries independently."""
        # User1 creates an entry
        self.client.login(username="user1", password="testpass123")
        self.client.post('/dashboard/time/create/', {
            'date': '2024-01-15',
            'hours': '8.0',
            'description': 'User1 work'
        })
        user1_entry = Time.objects.filter(description='User1 work').first()
        self.assertEqual(user1_entry.user, self.user1)
        print(f"✓ User1 created entry: {user1_entry.pk}")
        
        # User2 creates an entry
        self.client.login(username="user2", password="testpass123")
        self.client.post('/dashboard/time/create/', {
            'date': '2024-01-15',
            'hours': '6.0',
            'description': 'User2 work'
        })
        user2_entry = Time.objects.filter(description='User2 work').first()
        self.assertEqual(user2_entry.user, self.user2)
        print(f"✓ User2 created entry: {user2_entry.pk}")
        
        # User1 edits their entry
        self.client.login(username="user1", password="testpass123")
        self.client.post(f'/dashboard/time/{user1_entry.pk}/update/', {
            'date': '2024-01-16',
            'hours': '10.0',
            'description': 'User1 updated work'
        })
        user1_entry.refresh_from_db()
        self.assertEqual(user1_entry.user, self.user1)
        self.assertEqual(user1_entry.hours, 10.0)
        print(f"✓ User1 updated their entry, user preserved: {user1_entry.user.username}")
        
        # User2 edits their entry
        self.client.login(username="user2", password="testpass123")
        self.client.post(f'/dashboard/time/{user2_entry.pk}/update/', {
            'date': '2024-01-16',
            'hours': '7.0',
            'description': 'User2 updated work'
        })
        user2_entry.refresh_from_db()
        self.assertEqual(user2_entry.user, self.user2)
        self.assertEqual(user2_entry.hours, 7.0)
        print(f"✓ User2 updated their entry, user preserved: {user2_entry.user.username}")
        
        # Verify both entries are independent
        self.assertNotEqual(user1_entry.pk, user2_entry.pk)
        self.assertNotEqual(user1_entry.user, user2_entry.user)
        print("\n✅ Multiple users can work independently!")
