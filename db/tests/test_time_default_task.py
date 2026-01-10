"""Tests for Time model default task functionality."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from db.models import Task, Time

User = get_user_model()


class TimeDefaultTaskTest(TestCase):
    """Test that Time entries automatically get a default task."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_time_entry_gets_default_task_when_none_specified(self):
        """Test that a Time entry gets the default task when no task is specified."""
        # Create a time entry without specifying a task
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Test work",
        )

        # Refresh from database to ensure we have the latest data
        time_entry.refresh_from_db()

        # Verify that the time entry has a task assigned
        self.assertIsNotNone(time_entry.task)
        self.assertEqual(time_entry.task.name, "Default Task")

    def test_time_entry_keeps_custom_task_when_specified(self):
        """Test that a Time entry keeps a custom task when one is specified."""
        # Create a custom task
        custom_task = Task.objects.create(
            name="Custom Task",
            rate=100.00,
        )

        # Create a time entry with the custom task
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Test work with custom task",
            task=custom_task,
        )

        # Refresh from database
        time_entry.refresh_from_db()

        # Verify that the time entry has the custom task, not the default
        self.assertIsNotNone(time_entry.task)
        self.assertEqual(time_entry.task.name, "Custom Task")
        self.assertNotEqual(time_entry.task.name, "Default Task")

    def test_default_task_is_reused(self):
        """Test that the default task is created once and reused."""
        # Create multiple time entries without tasks
        time_entry1 = Time.objects.create(
            user=self.user,
            hours=4.0,
            description="First entry",
        )

        time_entry2 = Time.objects.create(
            user=self.user,
            hours=4.0,
            description="Second entry",
        )

        # Refresh from database
        time_entry1.refresh_from_db()
        time_entry2.refresh_from_db()

        # Both should have the same default task
        self.assertEqual(time_entry1.task, time_entry2.task)
        self.assertEqual(time_entry1.task.name, "Default Task")

        # Verify only one default task exists
        default_tasks = Task.objects.filter(name="Default Task")
        self.assertEqual(default_tasks.count(), 1)

    def test_updating_time_without_task_maintains_default(self):
        """Test that updating a time entry without a task maintains the default task."""
        # Create a time entry
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Initial work",
        )

        # Get the default task that was assigned
        default_task = time_entry.task
        self.assertIsNotNone(default_task)

        # Update the time entry (without changing the task)
        time_entry.hours = 10.0
        time_entry.description = "Updated work"
        time_entry.save()

        # Refresh from database
        time_entry.refresh_from_db()

        # Verify the default task is still assigned
        self.assertEqual(time_entry.task, default_task)

    def test_clearing_task_reassigns_default(self):
        """Test that clearing a task from a time entry reassigns the default."""
        # Create a custom task
        custom_task = Task.objects.create(
            name="Custom Task",
            rate=100.00,
        )

        # Create a time entry with the custom task
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Test work",
            task=custom_task,
        )

        # Verify custom task is assigned
        time_entry.refresh_from_db()
        self.assertEqual(time_entry.task, custom_task)

        # Clear the task
        time_entry.task = None
        time_entry.save()

        # Refresh from database
        time_entry.refresh_from_db()

        # Verify default task is assigned
        self.assertIsNotNone(time_entry.task)
        self.assertEqual(time_entry.task.name, "Default Task")
