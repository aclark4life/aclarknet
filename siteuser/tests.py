"""Tests for siteuser views."""

from decimal import Decimal

from django.test import Client, TestCase
from django.urls import reverse

from .models import SiteUser


class ProfileViewTests(TestCase):
    """Test user profile views."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = Client()
        self.user = SiteUser.objects.create_user(
            username="testuser",
            password="testpass123",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            rate=Decimal("100.00")
        )
    
    def test_profile_view_requires_login(self):
        """Test that profile view requires authentication."""
        response = self.client.get(reverse("profile_view"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_view_displays_user_info(self):
        """Test that profile view displays user information."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile_view"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertContains(response, "Test")
        self.assertContains(response, "User")
        self.assertContains(response, "test@example.com")
        self.assertContains(response, "$100.00")
    
    def test_profile_edit_view_requires_login(self):
        """Test that profile edit view requires authentication."""
        response = self.client.get(reverse("profile_edit"))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_profile_edit_view_displays_form(self):
        """Test that profile edit view displays the form."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile_edit"))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "first_name")
        self.assertContains(response, "last_name")
        self.assertContains(response, "email")
        self.assertContains(response, "rate")
    
    def test_profile_edit_updates_user_info(self):
        """Test that profile edit successfully updates user information."""
        self.client.login(username="testuser", password="testpass123")
        
        response = self.client.post(reverse("profile_edit"), {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
            "rate": "150.00"
        })
        
        # Should redirect to profile view after successful update
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile_view"))
        
        # Verify the user was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")
        self.assertEqual(self.user.email, "updated@example.com")
        self.assertEqual(self.user.rate, Decimal("150.00"))
    
    def test_profile_view_shows_profile_nav_active(self):
        """Test that profile view sets profile_nav in context."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile_view"))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["profile_nav"])
        self.assertTrue(response.context["dashboard"])

