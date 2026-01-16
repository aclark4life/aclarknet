"""Tests for Note generic foreign key functionality."""

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, RequestFactory

from db.models import Company, Client, Project, Note
from db.views.company import CompanyDetailView
from db.views.client import ClientDetailView
from db.views.project import ProjectDetailView

User = get_user_model()


class NoteGenericForeignKeyTest(TestCase):
    """Test that notes can be attached to any model via generic foreign key."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        
        # Create test objects
        self.company = Company.objects.create(name="Test Company")
        self.client = Client.objects.create(name="Test Client", company=self.company)
        self.project = Project.objects.create(name="Test Project", client=self.client)

    def test_note_can_be_attached_to_company(self):
        """Test that a note can be attached to a company."""
        content_type = ContentType.objects.get_for_model(Company)
        note = Note.objects.create(
            name="Company Note",
            text="This is a note about the company",
            user=self.user,
            content_type=content_type,
            object_id=str(self.company.pk)
        )
        
        self.assertEqual(note.content_object, self.company)
        
        # Verify note can be retrieved via filter
        notes = Note.objects.filter(
            content_type=content_type,
            object_id=str(self.company.pk)
        )
        self.assertEqual(notes.count(), 1)
        self.assertEqual(notes.first(), note)

    def test_note_can_be_attached_to_client(self):
        """Test that a note can be attached to a client."""
        content_type = ContentType.objects.get_for_model(Client)
        note = Note.objects.create(
            name="Client Note",
            text="This is a note about the client",
            user=self.user,
            content_type=content_type,
            object_id=str(self.client.pk)
        )
        
        self.assertEqual(note.content_object, self.client)

    def test_note_can_be_attached_to_project(self):
        """Test that a note can be attached to a project."""
        content_type = ContentType.objects.get_for_model(Project)
        note = Note.objects.create(
            name="Project Note",
            text="This is a note about the project",
            user=self.user,
            content_type=content_type,
            object_id=str(self.project.pk)
        )
        
        self.assertEqual(note.content_object, self.project)

    def test_multiple_notes_can_be_attached_to_same_object(self):
        """Test that multiple notes can be attached to the same object."""
        content_type = ContentType.objects.get_for_model(Company)
        
        note1 = Note.objects.create(
            name="Note 1",
            text="First note",
            user=self.user,
            content_type=content_type,
            object_id=str(self.company.pk)
        )
        
        note2 = Note.objects.create(
            name="Note 2",
            text="Second note",
            user=self.user,
            content_type=content_type,
            object_id=str(self.company.pk)
        )
        
        notes = Note.objects.filter(
            content_type=content_type,
            object_id=str(self.company.pk)
        )
        self.assertEqual(notes.count(), 2)
        self.assertIn(note1, notes)
        self.assertIn(note2, notes)

    def test_notes_appear_in_company_detail_view_context(self):
        """Test that notes appear in company detail view context."""
        content_type = ContentType.objects.get_for_model(Company)
        note = Note.objects.create(
            name="Company Note",
            text="This is a note about the company",
            user=self.user,
            content_type=content_type,
            object_id=str(self.company.pk)
        )
        
        request = self.factory.get(f'/company/{self.company.pk}/')
        request.user = self.user
        
        view = CompanyDetailView()
        view.request = request
        view.object = self.company
        view.kwargs = {'pk': self.company.pk}
        
        context = view.get_context_data()
        
        self.assertIn('object_notes', context)
        self.assertEqual(len(context['object_notes']), 1)
        self.assertEqual(context['object_notes'][0], note)

    def test_no_notes_context_when_no_notes_exist(self):
        """Test that object_notes is not in context when no notes exist."""
        request = self.factory.get(f'/company/{self.company.pk}/')
        request.user = self.user
        
        view = CompanyDetailView()
        view.request = request
        view.object = self.company
        view.kwargs = {'pk': self.company.pk}
        
        context = view.get_context_data()
        
        # object_notes should not be in context if no notes exist
        self.assertNotIn('object_notes', context)

    def test_note_without_generic_fk_still_works(self):
        """Test that notes can still be created without generic FK fields."""
        note = Note.objects.create(
            name="Standalone Note",
            text="This note is not attached to any object",
            user=self.user
        )
        
        self.assertIsNone(note.content_type)
        self.assertIsNone(note.object_id)
        self.assertIsNone(note.content_object)
