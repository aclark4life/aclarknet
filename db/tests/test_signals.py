from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from db.models import Time, Profile, Invoice, Project, Task, Client

User = get_user_model()


class TimeSignalTest(TestCase):
    """Test cases for Time model signals"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.profile = Profile.objects.create(user=self.user, mail=True)
        
    def test_time_creation_with_user_and_profile(self):
        """Test that creating a time entry with a user and profile works correctly"""
        with patch('db.signals.EmailMultiAlternatives.send') as mock_send:
            time_entry = Time.objects.create(
                user=self.user,
                hours=8.0,
                description="Test work"
            )
            # Email should be sent since user has a profile with mail=True
            mock_send.assert_called_once()
            self.assertIsNotNone(time_entry.id)
            
    def test_time_creation_with_user_no_profile(self):
        """Test that creating a time entry with a user but no profile doesn't crash"""
        # Create a user without a profile
        user_no_profile = User.objects.create_user(
            username="noprofileuser",
            email="noprofile@example.com",
            password="testpass123"
        )
        
        # This should not raise an AttributeError
        time_entry = Time.objects.create(
            user=user_no_profile,
            hours=8.0,
            description="Test work without profile"
        )
        self.assertIsNotNone(time_entry.id)
        
    def test_time_creation_with_none_user(self):
        """Test that creating a time entry with user=None doesn't crash"""
        # This should not raise an AttributeError
        time_entry = Time.objects.create(
            user=None,
            hours=8.0,
            description="Test work with no user"
        )
        self.assertIsNotNone(time_entry.id)
        
    def test_time_creation_with_user_profile_mail_false(self):
        """Test that creating a time entry with profile.mail=False doesn't send email"""
        # Update profile to disable email
        self.profile.mail = False
        self.profile.save()
        
        with patch('db.signals.EmailMultiAlternatives.send') as mock_send:
            time_entry = Time.objects.create(
                user=self.user,
                hours=8.0,
                description="Test work without email"
            )
            # Email should not be sent since profile.mail=False
            mock_send.assert_not_called()
            self.assertIsNotNone(time_entry.id)
