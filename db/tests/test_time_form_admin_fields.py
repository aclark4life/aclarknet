"""Tests for invoice and task field visibility on Time forms."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from db.forms import TimeForm

User = get_user_model()


class TimeFormAdminFieldsTest(TestCase):
    """Test that invoice and task fields are only visible to admin users."""

    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adminpass123",
        )
        self.regular_user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_admin_user_sees_invoice_and_task_fields(self):
        """Test that admin users see invoice and task fields."""
        form = TimeForm(user=self.admin_user)

        # Admin should see both invoice and task fields
        self.assertIn("invoice", form.fields)
        self.assertIn("task", form.fields)

    def test_regular_user_does_not_see_invoice_and_task_fields(self):
        """Test that regular users do not see invoice and task fields."""
        form = TimeForm(user=self.regular_user)

        # Regular user should not see invoice and task fields
        self.assertNotIn("invoice", form.fields)
        self.assertNotIn("task", form.fields)

    def test_regular_user_sees_other_fields(self):
        """Test that regular users still see other time entry fields."""
        form = TimeForm(user=self.regular_user)

        # Regular user should still see other fields
        self.assertIn("date", form.fields)
        self.assertIn("hours", form.fields)
        self.assertIn("description", form.fields)
        self.assertIn("project", form.fields)

    def test_regular_user_project_field_is_visible_not_hidden(self):
        """Test that the project field is a visible dropdown (not a
        HiddenInput) for regular users, unlike the invoice/task fields
        that are removed entirely."""
        form = TimeForm(user=self.regular_user)

        self.assertIn("project", form.fields)
        self.assertFalse(form.fields["project"].widget.is_hidden)

    def test_regular_user_project_field_lists_all_projects(self):
        """Test that the project dropdown is not scoped to the user;
        it lists every Project in the system, same as for admins."""
        from db.models import Client, Project

        client = Client.objects.create(name="Test Client")
        project_a = Project.objects.create(name="Project A", client=client)
        project_b = Project.objects.create(name="Project B", client=client)

        form = TimeForm(user=self.regular_user)
        queryset = form.fields["project"].queryset

        self.assertIn(project_a, queryset)
        self.assertIn(project_b, queryset)

    def test_form_without_user_shows_all_fields(self):
        """Test that form without user parameter shows all fields (backwards compatibility)."""
        form = TimeForm()

        # When no user is provided, all fields should be available
        self.assertIn("invoice", form.fields)
        self.assertIn("task", form.fields)
        self.assertIn("date", form.fields)
        self.assertIn("hours", form.fields)

    def test_form_layout_adapts_for_admin(self):
        """Test that form layout includes invoice and task for admins."""
        form = TimeForm(user=self.admin_user)

        # Check that the helper layout exists
        self.assertIsNotNone(form.helper.layout)
        # Both invoice and task should be in fields
        self.assertIn("invoice", form.fields)
        self.assertIn("task", form.fields)

    def test_form_layout_adapts_for_regular_user(self):
        """Test that form layout excludes invoice and task for regular users."""
        form = TimeForm(user=self.regular_user)

        # Check that the helper layout exists
        self.assertIsNotNone(form.helper.layout)
        # Invoice and task should not be in fields
        self.assertNotIn("invoice", form.fields)
        self.assertNotIn("task", form.fields)
