"""Tests for Time model default task functionality."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from db.models import Task, Time, Project, Profile

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


class TimeProjectDefaultTaskTest(TestCase):
    """Test that Time entries use project-specific default tasks."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        # Create a project-specific task
        self.project_task = Task.objects.create(
            name="Project Development",
            rate=150.00,
        )
        
        # Create a project with a default task
        self.project = Project.objects.create(
            name="Test Project",
            default_task=self.project_task,
        )

    def test_time_entry_uses_project_default_task(self):
        """Test that a Time entry uses the project's default task."""
        time_entry = Time.objects.create(
            user=self.user,
            project=self.project,
            hours=8.0,
            description="Project work",
        )

        time_entry.refresh_from_db()

        # Should use project's default task, not global default
        self.assertIsNotNone(time_entry.task)
        self.assertEqual(time_entry.task, self.project_task)
        self.assertEqual(time_entry.task.name, "Project Development")

    def test_explicit_task_overrides_project_default(self):
        """Test that explicitly setting a task overrides the project default."""
        custom_task = Task.objects.create(
            name="Custom Task",
            rate=200.00,
        )

        time_entry = Time.objects.create(
            user=self.user,
            project=self.project,
            task=custom_task,
            hours=8.0,
            description="Custom work",
        )

        time_entry.refresh_from_db()

        # Should use the explicitly set task
        self.assertEqual(time_entry.task, custom_task)
        self.assertNotEqual(time_entry.task, self.project_task)

    def test_project_without_default_uses_global_default(self):
        """Test that a project without a default task uses global default."""
        project_no_default = Project.objects.create(
            name="Project Without Default",
        )

        time_entry = Time.objects.create(
            user=self.user,
            project=project_no_default,
            hours=8.0,
            description="Generic work",
        )

        time_entry.refresh_from_db()

        # Should use global default task
        self.assertIsNotNone(time_entry.task)
        self.assertEqual(time_entry.task.name, "Default Task")


class TimeUserDefaultTaskTest(TestCase):
    """Test that Time entries use user-specific default tasks."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        
        # Create a user-specific task
        self.user_task = Task.objects.create(
            name="User Consulting",
            rate=175.00,
        )
        
        # Get or create profile and set default task
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        self.profile.default_task = self.user_task
        self.profile.save()

    def test_time_entry_uses_user_default_task(self):
        """Test that a Time entry uses the user's default task."""
        time_entry = Time.objects.create(
            user=self.user,
            hours=8.0,
            description="Consulting work",
        )

        time_entry.refresh_from_db()

        # Should use user's default task
        self.assertIsNotNone(time_entry.task)
        self.assertEqual(time_entry.task, self.user_task)
        self.assertEqual(time_entry.task.name, "User Consulting")

    def test_project_default_takes_priority_over_user_default(self):
        """Test that project default task takes priority over user default."""
        project_task = Task.objects.create(
            name="Project Priority",
            rate=200.00,
        )
        
        project = Project.objects.create(
            name="Priority Project",
            default_task=project_task,
        )

        time_entry = Time.objects.create(
            user=self.user,
            project=project,
            hours=8.0,
            description="Project work",
        )

        time_entry.refresh_from_db()

        # Should use project's default, not user's default
        self.assertEqual(time_entry.task, project_task)
        self.assertNotEqual(time_entry.task, self.user_task)

    def test_user_without_profile_default_uses_global_default(self):
        """Test that a user without a profile default uses global default."""
        user_no_default = User.objects.create_user(
            username="usernodefault",
            email="nodefault@example.com",
            password="testpass123",
        )

        time_entry = Time.objects.create(
            user=user_no_default,
            hours=8.0,
            description="Generic work",
        )

        time_entry.refresh_from_db()

        # Should use global default task
        self.assertIsNotNone(time_entry.task)
        self.assertEqual(time_entry.task.name, "Default Task")

