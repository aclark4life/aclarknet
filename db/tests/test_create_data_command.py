"""Tests for create_data management command."""

from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from db.models import Task, Invoice, Time, Client, Contact

User = get_user_model()


class CreateDataCommandTest(TestCase):
    """Test that create_data command generates real invoice data."""

    def test_task_rate_is_100(self):
        """Test that tasks are created with rate=$100."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=2",
            "--invoices=1",
            "--times=1",
            "--users=1",
            stdout=StringIO(),
        )

        # Check that tasks have rate=$100
        tasks = Task.objects.exclude(name="Default Task")
        self.assertTrue(tasks.exists())
        for task in tasks:
            self.assertEqual(task.rate, Decimal("100"))

    def test_time_amount_calculated_from_rate_and_hours(self):
        """Test that time entry amounts are calculated from rate * hours."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=2",
            "--invoices=1",
            "--times=5",
            "--users=1",
            stdout=StringIO(),
        )

        # Check that time entries have calculated amounts
        time_entries = Time.objects.all()
        for time_entry in time_entries:
            if time_entry.task and time_entry.task.rate:
                expected_amount = time_entry.task.rate * time_entry.hours
                self.assertEqual(
                    time_entry.amount,
                    expected_amount,
                    f"Time entry {time_entry.id}: expected {expected_amount}, got {time_entry.amount}",
                )

    def test_invoice_amount_calculated_from_time_entries(self):
        """Test that invoice amounts are calculated from sum of time entries."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=2",
            "--invoices=2",
            "--times=10",
            "--users=1",
            stdout=StringIO(),
        )

        # Check that invoice amounts match sum of their time entries
        invoices = Invoice.objects.all()
        for invoice in invoices:
            time_entries = Time.objects.filter(invoice=invoice)
            expected_amount = sum(
                (time.amount or Decimal("0")) for time in time_entries
            )
            self.assertEqual(
                invoice.amount,
                expected_amount,
                f"Invoice {invoice.id}: expected {expected_amount}, got {invoice.amount}",
            )

    def test_invoice_paid_amount_is_portion_of_total(self):
        """Test that invoice paid_amount is between 0 and the total amount."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=2",
            "--invoices=3",
            "--times=15",
            "--users=1",
            stdout=StringIO(),
        )

        # Check that paid amounts are reasonable
        invoices = Invoice.objects.all()
        for invoice in invoices:
            if invoice.amount > 0:
                self.assertGreaterEqual(invoice.paid_amount, Decimal("0"))
                self.assertLessEqual(invoice.paid_amount, invoice.amount)

    def test_default_task_rate_is_100(self):
        """Test that the default task is created with rate=$100."""
        # Get or create the default task
        default_task = Task.get_default_task()

        # Check that it has rate=$100
        self.assertEqual(default_task.name, "Default Task")
        self.assertEqual(default_task.rate, Decimal("100"))
        self.assertEqual(default_task.unit, Decimal("1.0"))

    def test_contacts_created_and_associated_with_clients(self):
        """Test that contacts are created and associated with clients."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=2",
            "--clients=3",
            "--contacts=5",
            "--projects=1",
            "--invoices=1",
            "--times=1",
            "--users=1",
            stdout=StringIO(),
        )

        # Check that contacts were created
        contacts = Contact.objects.all()
        self.assertEqual(contacts.count(), 5, "Should create 5 contacts")

        # Check that all contacts are associated with clients
        for contact in contacts:
            self.assertIsNotNone(
                contact.client, "Contact should be associated with a client"
            )
            self.assertIn(
                contact.client,
                Client.objects.all(),
                "Contact should be associated with an existing client",
            )

        # Check that contacts have required fields populated
        for contact in contacts:
            self.assertTrue(
                contact.first_name or contact.last_name,
                "Contact should have at least first or last name",
            )
            self.assertIsNotNone(contact.email, "Contact should have email")

    def test_users_created_with_mail_enabled(self):
        """Test that users are created with mail=True to enable email notifications."""
        # Run the command with minimal data
        call_command(
            "create_data",
            "--companies=1",
            "--clients=1",
            "--projects=1",
            "--invoices=1",
            "--times=1",
            "--users=3",
            stdout=StringIO(),
        )

        # Check that users were created with mail=True
        users = User.objects.all()
        self.assertGreaterEqual(users.count(), 3, "Should create at least 3 users")

        # Verify all users have mail enabled
        for user in users:
            self.assertTrue(
                user.mail,
                f"User {user.username} should have mail=True to receive email notifications",
            )

    def test_users_only_flag(self):
        """Test that --users-only flag creates only users."""
        # Run the command with --users-only flag
        call_command(
            "create_data",
            "--users-only=5",
            stdout=StringIO(),
        )

        # Check that only users were created
        users = User.objects.all()
        self.assertEqual(users.count(), 5, "Should create 5 users")
        
        # Verify no other models were created
        from db.models import Company, Client, Project, Invoice, Time
        self.assertEqual(Company.objects.count(), 0, "Should not create companies")
        self.assertEqual(Client.objects.count(), 0, "Should not create clients")
        self.assertEqual(Project.objects.count(), 0, "Should not create projects")
        self.assertEqual(Invoice.objects.count(), 0, "Should not create invoices")
        self.assertEqual(Time.objects.count(), 0, "Should not create time entries")

    def test_companies_only_flag(self):
        """Test that --companies-only flag creates only companies."""
        # Run the command with --companies-only flag
        call_command(
            "create_data",
            "--companies-only=3",
            stdout=StringIO(),
        )

        # Check that only companies were created
        from db.models import Company, Client, Project, Invoice, Time
        self.assertEqual(Company.objects.count(), 3, "Should create 3 companies")
        
        # Verify no other models were created
        self.assertEqual(User.objects.count(), 0, "Should not create users")
        self.assertEqual(Client.objects.count(), 0, "Should not create clients")
        self.assertEqual(Project.objects.count(), 0, "Should not create projects")
        self.assertEqual(Invoice.objects.count(), 0, "Should not create invoices")
        self.assertEqual(Time.objects.count(), 0, "Should not create time entries")

    def test_clients_only_flag_creates_dependencies(self):
        """Test that --clients-only flag creates clients and required companies."""
        # Run the command with --clients-only flag
        call_command(
            "create_data",
            "--clients-only=4",
            stdout=StringIO(),
        )

        # Check that clients were created
        from db.models import Company, Client, Project, Invoice, Time
        self.assertEqual(Client.objects.count(), 4, "Should create 4 clients")
        
        # Verify companies were created as dependencies
        self.assertGreater(Company.objects.count(), 0, "Should create companies as dependencies")
        
        # Verify other models were not created
        self.assertEqual(User.objects.count(), 0, "Should not create users")
        self.assertEqual(Project.objects.count(), 0, "Should not create projects")
        self.assertEqual(Invoice.objects.count(), 0, "Should not create invoices")
        self.assertEqual(Time.objects.count(), 0, "Should not create time entries")

    def test_times_only_flag_creates_dependencies(self):
        """Test that --times-only flag creates time entries and all required dependencies."""
        # Run the command with --times-only flag
        call_command(
            "create_data",
            "--times-only=10",
            stdout=StringIO(),
        )

        # Check that time entries were created
        from db.models import Company, Client, Project, Invoice, Time
        self.assertEqual(Time.objects.count(), 10, "Should create 10 time entries")
        
        # Verify all dependencies were created
        self.assertGreater(Company.objects.count(), 0, "Should create companies as dependencies")
        self.assertGreater(Client.objects.count(), 0, "Should create clients as dependencies")
        self.assertGreater(Project.objects.count(), 0, "Should create projects as dependencies")
        self.assertGreater(Invoice.objects.count(), 0, "Should create invoices as dependencies")
        self.assertGreater(User.objects.count(), 0, "Should create users as dependencies")
        self.assertGreater(Task.objects.count(), 0, "Should create tasks as dependencies")
