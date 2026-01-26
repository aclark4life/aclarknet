"""Tests for the CMS app."""

from django.test import TestCase
from django.urls import reverse

from .forms import ContactFormPublic


class ContactFormTests(TestCase):
    """Tests for the public contact form."""

    def test_contact_form_has_required_fields(self):
        """Test that the contact form has all required fields."""
        form = ContactFormPublic()
        self.assertIn("name", form.fields)
        self.assertIn("email", form.fields)
        self.assertIn("how_did_you_hear_about_us", form.fields)
        self.assertIn("how_can_we_help", form.fields)

    def test_contact_form_valid_data(self):
        """Test form with valid data."""
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "how_did_you_hear_about_us": "Internet search engine",
            "how_can_we_help": "I need help with my project",
        }
        form = ContactFormPublic(data=form_data)
        self.assertTrue(form.is_valid())

    def test_contact_form_missing_required_field(self):
        """Test form with missing required field."""
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            # Missing how_did_you_hear_about_us and how_can_we_help
        }
        form = ContactFormPublic(data=form_data)
        self.assertFalse(form.is_valid())

    def test_contact_form_invalid_email(self):
        """Test form with invalid email."""
        form_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "how_did_you_hear_about_us": "Internet search engine",
            "how_can_we_help": "I need help with my project",
        }
        form = ContactFormPublic(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class ContactViewTests(TestCase):
    """Tests for the contact view."""

    def test_contact_page_loads(self):
        """Test that the contact page loads successfully."""
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")

    def test_contact_page_contains_form(self):
        """Test that the contact page contains the form."""
        response = self.client.get(reverse("contact"))
        self.assertContains(response, '<form')
        self.assertContains(response, 'method="POST"')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contact_form_submission_success(self):
        """Test successful form submission."""
        form_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "how_did_you_hear_about_us": "Internet search engine",
            "how_can_we_help": "I need help with my project",
        }
        response = self.client.post(reverse("contact"), data=form_data)
        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)

    def test_contact_form_submission_invalid_data(self):
        """Test form submission with invalid data."""
        form_data = {
            "name": "",  # Empty name
            "email": "john@example.com",
            "how_did_you_hear_about_us": "Internet search engine",
            "how_can_we_help": "I need help with my project",
        }
        response = self.client.post(reverse("contact"), data=form_data)
        # Should return to form with errors (status 200)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "name", "This field is required.")

