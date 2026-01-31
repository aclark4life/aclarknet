"""Tests for the CMS app."""

import os
from unittest.mock import patch
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .forms import ContactFormPublic


class ContactFormTests(TestCase):
    """Tests for the public contact form."""

    def setUp(self):
        """Set up test environment."""
        # Disable reCAPTCHA for tests
        os.environ["RECAPTCHA_DISABLE"] = "True"

    def tearDown(self):
        """Clean up test environment."""
        # Remove the environment variable
        if "RECAPTCHA_DISABLE" in os.environ:
            del os.environ["RECAPTCHA_DISABLE"]

    def test_contact_form_has_required_fields(self):
        """Test that the contact form has all required fields."""
        form = ContactFormPublic()
        self.assertIn("name", form.fields)
        self.assertIn("email", form.fields)
        self.assertIn("how_did_you_hear_about_us", form.fields)
        self.assertIn("how_can_we_help", form.fields)
        self.assertIn("captcha", form.fields)

    @patch("django_recaptcha.fields.ReCaptchaField.validate", return_value=True)
    def test_contact_form_valid_data(self, mock_validate):
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

    def setUp(self):
        """Set up test environment."""
        # Disable reCAPTCHA for tests
        os.environ["RECAPTCHA_DISABLE"] = "True"

    def tearDown(self):
        """Clean up test environment."""
        # Remove the environment variable
        if "RECAPTCHA_DISABLE" in os.environ:
            del os.environ["RECAPTCHA_DISABLE"]

    def test_contact_page_loads(self):
        """Test that the contact page loads successfully."""
        response = self.client.get(reverse("contact"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")

    def test_contact_page_contains_form(self):
        """Test that the contact page contains the form."""
        response = self.client.get(reverse("contact"))
        self.assertContains(response, "<form")
        self.assertContains(response, 'method="POST"')
        self.assertContains(response, "csrfmiddlewaretoken")

    @patch("django_recaptcha.fields.ReCaptchaField.validate", return_value=True)
    def test_contact_form_submission_success(self, mock_validate):
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
        self.assertFormError(
            response.context["form"], "name", "This field is required."
        )

    @patch("django_recaptcha.fields.ReCaptchaField.validate", return_value=True)
    def test_contact_form_submission_creates_note(self, mock_validate):
        """Test that contact form submission creates a Note."""
        from db.models import Note

        # Get initial count of notes
        initial_count = Note.objects.count()

        form_data = {
            "name": "Jane Smith",
            "email": "jane@example.com",
            "how_did_you_hear_about_us": "Social media",
            "how_can_we_help": "I would like to discuss a potential project",
        }
        response = self.client.post(reverse("contact"), data=form_data)

        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)

        # Check that a Note was created
        self.assertEqual(Note.objects.count(), initial_count + 1)

        # Verify the Note contains the correct information
        note = Note.objects.latest("created")
        self.assertIn("Jane Smith", note.name)
        self.assertIn("jane@example.com", note.description)
        self.assertIn("Social media", note.description)
        self.assertIn("I would like to discuss a potential project", note.description)

    @patch("django_recaptcha.fields.ReCaptchaField.validate", return_value=True)
    def test_contact_form_submission_sends_email(self, mock_validate):
        """Test that contact form submission sends an email notification."""
        form_data = {
            "name": "Bob Johnson",
            "email": "bob@example.com",
            "how_did_you_hear_about_us": "Referral from a friend or family member",
            "how_can_we_help": "I have a question about your services",
        }

        # Submit the form
        response = self.client.post(reverse("contact"), data=form_data)

        # Should redirect after successful submission
        self.assertEqual(response.status_code, 302)

        # Check that one email was sent
        self.assertEqual(len(mail.outbox), 1)

        # Verify email details
        email = mail.outbox[0]
        self.assertEqual(email.subject, "Contact Form Submission from Bob Johnson")
        self.assertIn("Bob Johnson", email.body)
        self.assertIn("bob@example.com", email.body)
        self.assertIn("Referral from a friend or family member", email.body)
        self.assertIn("I have a question about your services", email.body)
        self.assertEqual(email.to, ["aclark@aclark.net"])
        self.assertEqual(email.from_email, "aclark@aclark.net")
