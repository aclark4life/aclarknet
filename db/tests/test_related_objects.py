"""Tests for related objects display in detail views."""

from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

from db.models import Company, Client, Project, Task, Time, Invoice, Contact
from db.views.time import TimeDetailView
from db.views.task import TaskDetailView
from db.views.invoice import InvoiceDetailView
from db.views.contact import ContactDetailView

User = get_user_model()


class TimeDetailViewRelatedObjectsTest(TestCase):
    """Test that Time detail view shows all related objects."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        
        # Create full hierarchy
        self.company = Company.objects.create(name="Test Company")
        self.client = Client.objects.create(name="Test Client", company=self.company)
        self.project = Project.objects.create(name="Test Project", client=self.client)
        self.task = Task.objects.create(name="Test Task", project=self.project)
        self.invoice = Invoice.objects.create(name="Test Invoice", project=self.project)
        self.time = Time.objects.create(
            user=self.user,
            project=self.project,
            task=self.task,
            invoice=self.invoice,
            hours=8.0,
            description="Test work",
        )

    def test_time_shows_invoice(self):
        """Test that Time detail view includes related invoice."""
        request = self.factory.get(f'/time/{self.time.pk}/')
        request.user = self.user
        
        view = TimeDetailView()
        view.request = request
        view.object = self.time
        view.kwargs = {'pk': self.time.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        # page_obj is a list when not paginated
        self.assertIn(self.invoice, page_obj)

    def test_time_shows_project(self):
        """Test that Time detail view includes related project."""
        request = self.factory.get(f'/time/{self.time.pk}/')
        request.user = self.user
        
        view = TimeDetailView()
        view.request = request
        view.object = self.time
        view.kwargs = {'pk': self.time.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.project, page_obj)

    def test_time_shows_client(self):
        """Test that Time detail view includes related client."""
        request = self.factory.get(f'/time/{self.time.pk}/')
        request.user = self.user
        
        view = TimeDetailView()
        view.request = request
        view.object = self.time
        view.kwargs = {'pk': self.time.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.client, page_obj)

    def test_time_shows_company(self):
        """Test that Time detail view includes related company."""
        request = self.factory.get(f'/time/{self.time.pk}/')
        request.user = self.user
        
        view = TimeDetailView()
        view.request = request
        view.object = self.time
        view.kwargs = {'pk': self.time.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.company, page_obj)

    def test_time_without_relationships_shows_no_related(self):
        """Test that Time without relationships shows no related objects."""
        time_no_relations = Time.objects.create(
            user=self.user,
            hours=4.0,
            description="Independent work",
        )
        
        request = self.factory.get(f'/time/{time_no_relations.pk}/')
        request.user = self.user
        
        view = TimeDetailView()
        view.request = request
        view.object = time_no_relations
        view.kwargs = {'pk': time_no_relations.pk}
        
        context = view.get_context_data()
        
        self.assertFalse(context.get('has_related', False))


class TaskDetailViewRelatedObjectsTest(TestCase):
    """Test that Task detail view shows all related objects."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        
        # Create full hierarchy
        self.company = Company.objects.create(name="Test Company")
        self.client = Client.objects.create(name="Test Client", company=self.company)
        self.project = Project.objects.create(name="Test Project", client=self.client)
        self.task = Task.objects.create(name="Test Task", project=self.project)

    def test_task_shows_project(self):
        """Test that Task detail view includes related project."""
        request = self.factory.get(f'/task/{self.task.pk}/')
        request.user = self.user
        
        view = TaskDetailView()
        view.request = request
        view.object = self.task
        view.kwargs = {'pk': self.task.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.project, page_obj)

    def test_task_shows_client(self):
        """Test that Task detail view includes related client."""
        request = self.factory.get(f'/task/{self.task.pk}/')
        request.user = self.user
        
        view = TaskDetailView()
        view.request = request
        view.object = self.task
        view.kwargs = {'pk': self.task.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.client, page_obj)

    def test_task_shows_company(self):
        """Test that Task detail view includes related company."""
        request = self.factory.get(f'/task/{self.task.pk}/')
        request.user = self.user
        
        view = TaskDetailView()
        view.request = request
        view.object = self.task
        view.kwargs = {'pk': self.task.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.company, page_obj)


class InvoiceDetailViewRelatedObjectsTest(TestCase):
    """Test that Invoice detail view shows all related objects including company."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        
        # Create full hierarchy
        self.company = Company.objects.create(name="Test Company")
        self.client = Client.objects.create(name="Test Client", company=self.company)
        self.project = Project.objects.create(name="Test Project", client=self.client)
        self.invoice = Invoice.objects.create(name="Test Invoice", project=self.project)

    def test_invoice_shows_company(self):
        """Test that Invoice detail view includes related company."""
        request = self.factory.get(f'/invoice/{self.invoice.pk}/')
        request.user = self.user
        
        view = InvoiceDetailView()
        view.request = request
        view.object = self.invoice
        view.kwargs = {'pk': self.invoice.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.company, page_obj)


class ContactDetailViewRelatedObjectsTest(TestCase):
    """Test that Contact detail view shows all related objects."""

    def setUp(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123",
        )
        
        # Create hierarchy
        self.company = Company.objects.create(name="Test Company")
        self.client = Client.objects.create(name="Test Client", company=self.company)
        self.contact = Contact.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            client=self.client,
        )

    def test_contact_shows_client(self):
        """Test that Contact detail view includes related client."""
        request = self.factory.get(f'/contact/{self.contact.pk}/')
        request.user = self.user
        
        view = ContactDetailView()
        view.request = request
        view.object = self.contact
        view.kwargs = {'pk': self.contact.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.client, page_obj)

    def test_contact_shows_company(self):
        """Test that Contact detail view includes related company."""
        request = self.factory.get(f'/contact/{self.contact.pk}/')
        request.user = self.user
        
        view = ContactDetailView()
        view.request = request
        view.object = self.contact
        view.kwargs = {'pk': self.contact.pk}
        
        context = view.get_context_data()
        
        self.assertTrue(context['has_related'])
        page_obj = context.get('page_obj', [])
        self.assertIn(self.company, page_obj)
