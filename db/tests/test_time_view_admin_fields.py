"""Tests for TimeCreateView and TimeUpdateView with admin field restrictions."""

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock

from db.models import Time
from db.views.time import TimeCreateView, TimeUpdateView

User = get_user_model()


class TimeViewAdminFieldsTest(TestCase):
    """Test that views pass the user to forms correctly."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
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

    def test_time_create_view_passes_user_to_form(self):
        """Test that TimeCreateView passes user to form."""
        view = TimeCreateView()
        request = self.factory.get('/time/create/')
        request.user = self.regular_user
        view.request = request
        
        # Get form kwargs
        kwargs = view.get_form_kwargs()
        
        # User should be in kwargs
        self.assertIn('user', kwargs)
        self.assertEqual(kwargs['user'], self.regular_user)

    def test_time_create_view_admin_user_gets_all_fields(self):
        """Test that admin users get forms with all fields."""
        view = TimeCreateView()
        request = self.factory.get('/time/create/')
        request.user = self.admin_user
        view.request = request
        view.object = None
        
        # Get the form
        form = view.get_form()
        
        # Admin should see invoice and task fields
        self.assertIn('invoice', form.fields)
        self.assertIn('task', form.fields)

    def test_time_create_view_regular_user_restricted_fields(self):
        """Test that regular users get forms without invoice/task fields."""
        view = TimeCreateView()
        request = self.factory.get('/time/create/')
        request.user = self.regular_user
        view.request = request
        view.object = None
        
        # Get the form
        form = view.get_form()
        
        # Regular user should not see invoice and task fields
        self.assertNotIn('invoice', form.fields)
        self.assertNotIn('task', form.fields)

    def test_time_update_view_passes_user_to_form(self):
        """Test that TimeUpdateView passes user to form."""
        # Create a time entry
        time_entry = Time.objects.create(
            user=self.regular_user,
            hours=8.0,
            description="Test work"
        )
        
        view = TimeUpdateView()
        request = self.factory.get(f'/time/{time_entry.pk}/update/')
        request.user = self.regular_user
        view.request = request
        view.kwargs = {'pk': str(time_entry.pk)}
        
        # Get form kwargs
        kwargs = view.get_form_kwargs()
        
        # User should be in kwargs
        self.assertIn('user', kwargs)
        self.assertEqual(kwargs['user'], self.regular_user)

    def test_time_update_view_admin_user_gets_all_fields(self):
        """Test that admin users get update forms with all fields."""
        # Create a time entry
        time_entry = Time.objects.create(
            user=self.admin_user,
            hours=8.0,
            description="Test work"
        )
        
        view = TimeUpdateView()
        request = self.factory.get(f'/time/{time_entry.pk}/update/')
        request.user = self.admin_user
        view.request = request
        view.kwargs = {'pk': str(time_entry.pk)}
        view.object = time_entry
        
        # Get the form
        form = view.get_form()
        
        # Admin should see invoice and task fields
        self.assertIn('invoice', form.fields)
        self.assertIn('task', form.fields)

    def test_time_update_view_regular_user_restricted_fields(self):
        """Test that regular users get update forms without invoice/task fields."""
        # Create a time entry
        time_entry = Time.objects.create(
            user=self.regular_user,
            hours=8.0,
            description="Test work"
        )
        
        view = TimeUpdateView()
        request = self.factory.get(f'/time/{time_entry.pk}/update/')
        request.user = self.regular_user
        view.request = request
        view.kwargs = {'pk': str(time_entry.pk)}
        view.object = time_entry
        
        # Get the form
        form = view.get_form()
        
        # Regular user should not see invoice and task fields
        self.assertNotIn('invoice', form.fields)
        self.assertNotIn('task', form.fields)
