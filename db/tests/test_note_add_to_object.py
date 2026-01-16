"""Tests for adding notes to objects via the UI."""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.urls import reverse

from db.models import Company, Note

User = get_user_model()


class NoteAddToObjectViewTest(TestCase):
    """Test the note_add_to_object view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="testpass123",
        )
        self.client.login(username="admin", password="testpass123")
        
        # Create test company
        self.company = Company.objects.create(name="Test Company")
        self.content_type = ContentType.objects.get_for_model(Company)

    def test_add_note_view_get(self):
        """Test GET request to add note view."""
        url = reverse('note_add_to_object')
        response = self.client.get(
            url,
            {
                'content_type': self.content_type.id,
                'object_id': str(self.company.pk)
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Note')

    def test_add_note_view_post(self):
        """Test POST request to add note view."""
        url = reverse('note_add_to_object')
        
        initial_note_count = Note.objects.filter(
            content_type=self.content_type,
            object_id=str(self.company.pk)
        ).count()
        
        response = self.client.post(
            url,
            {
                'name': 'Test Note',
                'text': 'This is a test note',
                'content_type': self.content_type.id,
                'object_id': str(self.company.pk),
                'user': self.user.id,
            }
        )
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Check that note was created
        final_note_count = Note.objects.filter(
            content_type=self.content_type,
            object_id=str(self.company.pk)
        ).count()
        
        self.assertEqual(final_note_count, initial_note_count + 1)
        
        # Verify note content
        note = Note.objects.filter(
            content_type=self.content_type,
            object_id=str(self.company.pk)
        ).first()
        
        self.assertEqual(note.name, 'Test Note')
        self.assertEqual(note.text, 'This is a test note')
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.content_object, self.company)

    def test_add_note_redirects_to_object(self):
        """Test that adding a note redirects back to the object."""
        url = reverse('note_add_to_object')
        
        response = self.client.post(
            url,
            {
                'name': 'Test Note',
                'text': 'This is a test note',
                'content_type': self.content_type.id,
                'object_id': str(self.company.pk),
                'user': self.user.id,
            }
        )
        
        # Should redirect to company detail view
        expected_url = reverse('company_view', args=[self.company.pk])
        self.assertRedirects(response, expected_url, fetch_redirect_response=False)

    def test_company_detail_view_shows_add_note_button(self):
        """Test that company detail view shows the Add Note button."""
        url = reverse('company_view', args=[self.company.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Note')
        self.assertContains(response, 'note_add_to_object')

    def test_company_detail_view_shows_notes_section(self):
        """Test that company detail view shows notes section."""
        # Create a note
        Note.objects.create(
            name='Test Note',
            text='This is a test note',
            user=self.user,
            content_type=self.content_type,
            object_id=str(self.company.pk)
        )
        
        url = reverse('company_view', args=[self.company.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notes')
        self.assertContains(response, 'Test Note')
        self.assertContains(response, 'This is a test note')

    def test_add_note_without_name(self):
        """Test adding a note without a name (name is optional)."""
        url = reverse('note_add_to_object')
        
        response = self.client.post(
            url,
            {
                'text': 'This is a test note without a name',
                'content_type': self.content_type.id,
                'object_id': str(self.company.pk),
                'user': self.user.id,
            }
        )
        
        self.assertEqual(response.status_code, 302)
        
        note = Note.objects.filter(
            content_type=self.content_type,
            object_id=str(self.company.pk)
        ).first()
        
        self.assertIsNotNone(note)
        self.assertEqual(note.text, 'This is a test note without a name')
        self.assertEqual(note.name, '')
