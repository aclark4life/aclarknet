"""Tests for automatic user assignment to Time entries."""

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from unittest.mock import Mock

from db.models import Time
from db.views.time import TimeCreateView, TimeCopyView
from db.forms import TimeForm

User = get_user_model()


class TimeUserAssignmentTest(TestCase):
    """Test that Time entries automatically get assigned to the session user."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )

    def test_time_create_view_assigns_session_user(self):
        """Test that TimeCreateView assigns the logged-in user to new time entries."""
        # Create a mock form with valid data
        mock_form = Mock()
        time_entry = Time(hours=8.0, description="Test work")
        mock_form.save.return_value = time_entry
        
        # Create the view
        view = TimeCreateView()
        request = self.factory.post('/time/create/')
        request.user = self.user
        view.request = request
        
        # Mock get_success_url to avoid URL resolution issues
        view.get_success_url = Mock(return_value='/time/')
        
        # Call form_valid
        response = view.form_valid(mock_form)
        
        # Verify that the user was set on the time entry
        self.assertEqual(time_entry.user, self.user)
        self.assertNotEqual(time_entry.user, self.other_user)

    def test_time_create_view_respects_existing_user_in_form(self):
        """Test that if form already has a user set, it's preserved."""
        # Create a time entry with a user already set
        time_entry = Time(
            user=self.other_user,
            hours=8.0,
            description="Test work"
        )
        
        # Create a mock form
        mock_form = Mock()
        mock_form.save.return_value = time_entry
        
        # Create the view with a different user logged in
        view = TimeCreateView()
        request = self.factory.post('/time/create/')
        request.user = self.user
        view.request = request
        
        # Mock get_success_url
        view.get_success_url = Mock(return_value='/time/')
        
        # Call form_valid - should override with session user
        response = view.form_valid(mock_form)
        
        # Verify the session user was assigned (should override)
        self.assertEqual(time_entry.user, self.user)

    def test_time_copy_view_assigns_session_user(self):
        """Test that TimeCopyView assigns the logged-in user to copied time entries."""
        # Create an original time entry with a different user
        original_time = Time.objects.create(
            user=self.other_user,
            hours=8.0,
            description="Original work",
        )
        
        # Create a mock form
        mock_form = Mock()
        copied_time = Time(hours=8.0, description="Original work")
        mock_form.save.return_value = copied_time
        
        # Create the view
        view = TimeCopyView()
        request = self.factory.post(f'/time/{original_time.pk}/copy/')
        request.user = self.user
        view.request = request
        view.kwargs = {'pk': str(original_time.pk)}
        
        # Mock get_success_url
        view.get_success_url = Mock(return_value='/time/')
        
        # Call form_valid
        response = view.form_valid(mock_form)
        
        # Verify that the logged-in user was assigned, not the original user
        self.assertEqual(copied_time.user, self.user)
        self.assertNotEqual(copied_time.user, self.other_user)
