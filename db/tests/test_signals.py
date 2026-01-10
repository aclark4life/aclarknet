from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from db.models import Time, Profile, Invoice, Task, Project, Client

User = get_user_model()


class TimeSignalTest(TestCase):
    """Test cases for Time model signals"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(user=self.user, mail=True)

    def test_time_creation_with_user_and_profile(self):
        """Test that creating a time entry with a user and profile works correctly"""
        with patch("db.signals.EmailMultiAlternatives.send") as mock_send:
            time_entry = Time.objects.create(
                user=self.user, hours=8.0, description="Test work"
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
            password="testpass123",
        )

        # This should not raise an AttributeError
        time_entry = Time.objects.create(
            user=user_no_profile, hours=8.0, description="Test work without profile"
        )
        self.assertIsNotNone(time_entry.id)

    def test_time_creation_with_none_user(self):
        """Test that creating a time entry with user=None doesn't crash"""
        # This should not raise an AttributeError
        time_entry = Time.objects.create(
            user=None, hours=8.0, description="Test work with no user"
        )
        self.assertIsNotNone(time_entry.id)

    def test_time_creation_with_user_profile_mail_false(self):
        """Test that creating a time entry with profile.mail=False doesn't send email"""
        # Update profile to disable email
        self.profile.mail = False
        self.profile.save()

        with patch("db.signals.EmailMultiAlternatives.send") as mock_send:
            time_entry = Time.objects.create(
                user=self.user, hours=8.0, description="Test work without email"
            )
            # Email should not be sent since profile.mail=False
            mock_send.assert_not_called()
            self.assertIsNotNone(time_entry.id)


class InvoiceRecalculationSignalTest(TestCase):
    """Test cases for invoice amount recalculation via signals"""

    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = Profile.objects.create(
            user=self.user, rate=Decimal("100.00"), mail=False
        )
        self.client = Client.objects.create(name="Test Client")
        self.project = Project.objects.create(name="Test Project", client=self.client)
        self.task = Task.objects.create(name="Test Task", rate=Decimal("150.00"))
        self.invoice = Invoice.objects.create(
            subject="Test Invoice", project=self.project
        )

    def test_invoice_amount_calculated_on_time_creation(self):
        """Test that invoice amount is calculated when a time entry is created"""
        # Create a time entry associated with the invoice
        with patch("db.signals.EmailMultiAlternatives.send"):
            time_entry = Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("5.0"),
                invoice=self.invoice,
                description="Test work",
            )

        # Refresh the invoice from database
        self.invoice.refresh_from_db()

        # Expected amount: 5 hours * $150/hour = $750
        self.assertEqual(
            self.invoice.amount,
            Decimal("750.00"),
            f"Invoice amount should be $750.00, got {self.invoice.amount}",
        )

    def test_invoice_amount_updated_on_time_edit(self):
        """Test that invoice amount is updated when a time entry is edited"""
        # Create initial time entry
        with patch("db.signals.EmailMultiAlternatives.send"):
            time_entry = Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("5.0"),
                invoice=self.invoice,
                description="Test work",
            )

        # Verify initial amount
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount, Decimal("750.00"))

        # Update the time entry hours
        time_entry.hours = Decimal("10.0")
        time_entry.save()

        # Refresh and verify updated amount: 10 hours * $150/hour = $1500
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.amount,
            Decimal("1500.00"),
            f"Invoice amount should be $1500.00 after update, got {self.invoice.amount}",
        )

    def test_invoice_amount_updated_on_time_deletion(self):
        """Test that invoice amount is updated when a time entry is deleted"""
        # Create two time entries
        with patch("db.signals.EmailMultiAlternatives.send"):
            time_entry1 = Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("5.0"),
                invoice=self.invoice,
                description="Test work 1",
            )
            time_entry2 = Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("3.0"),
                invoice=self.invoice,
                description="Test work 2",
            )

        # Verify total amount: (5 + 3) hours * $150/hour = $1200
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount, Decimal("1200.00"))

        # Delete one time entry
        time_entry1.delete()

        # Verify updated amount: 3 hours * $150/hour = $450
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.amount,
            Decimal("450.00"),
            f"Invoice amount should be $450.00 after deletion, got {self.invoice.amount}",
        )

    def test_invoice_amount_with_multiple_time_entries(self):
        """Test invoice amount calculation with multiple time entries"""
        # Create multiple time entries with different hours
        with patch("db.signals.EmailMultiAlternatives.send"):
            Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("2.0"),
                invoice=self.invoice,
                description="Work 1",
            )
            Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("4.5"),
                invoice=self.invoice,
                description="Work 2",
            )
            Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("1.5"),
                invoice=self.invoice,
                description="Work 3",
            )

        # Verify total: (2 + 4.5 + 1.5) hours * $150/hour = $1200
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.amount, Decimal("1200.00"))

    def test_invoice_amount_with_no_task(self):
        """Test that invoice handles time entries without a task gracefully"""
        # Create time entry without a task (should use default task)
        with patch("db.signals.EmailMultiAlternatives.send"):
            time_entry = Time.objects.create(
                user=self.user,
                hours=Decimal("5.0"),
                invoice=self.invoice,
                description="Test work without explicit task",
            )

        # The time entry should have been assigned a default task by the Time.save() method
        self.assertIsNotNone(
            time_entry.task, "Time entry should have been assigned a default task"
        )

        # Refresh invoice and verify it has an amount calculated
        self.invoice.refresh_from_db()
        self.assertIsNotNone(
            self.invoice.amount, "Invoice should have an amount even with default task"
        )

    def test_invoice_cost_and_net_calculated(self):
        """Test that invoice cost and net are calculated correctly"""
        # Create time entry
        with patch("db.signals.EmailMultiAlternatives.send"):
            Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("5.0"),
                invoice=self.invoice,
                description="Test work",
            )

        # Refresh invoice
        self.invoice.refresh_from_db()

        # Expected: amount = 5 * $150 = $750, cost = 5 * $100 = $500, net = $250
        self.assertEqual(self.invoice.amount, Decimal("750.00"))
        self.assertEqual(self.invoice.cost, Decimal("500.00"))
        self.assertEqual(self.invoice.net, Decimal("250.00"))

    def test_invoice_hours_calculated(self):
        """Test that total hours are calculated correctly"""
        # Create multiple time entries
        with patch("db.signals.EmailMultiAlternatives.send"):
            Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("3.5"),
                invoice=self.invoice,
                description="Work 1",
            )
            Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("2.5"),
                invoice=self.invoice,
                description="Work 2",
            )

        # Refresh invoice
        self.invoice.refresh_from_db()

        # Verify total hours: 3.5 + 2.5 = 6.0
        self.assertEqual(self.invoice.hours, Decimal("6.00"))

    def test_invoice_recalculation_on_invoice_save(self):
        """Test that invoice amounts are recalculated when invoice is saved"""
        # Create time entries first
        with patch("db.signals.EmailMultiAlternatives.send"):
            Time.objects.create(
                user=self.user,
                task=self.task,
                hours=Decimal("5.0"),
                invoice=self.invoice,
                description="Test work",
            )

        # Manually change invoice amount to incorrect value
        self.invoice.amount = Decimal("0.00")
        self.invoice.save()

        # Refresh and verify it was recalculated correctly
        self.invoice.refresh_from_db()
        self.assertEqual(
            self.invoice.amount,
            Decimal("750.00"),
            "Invoice amount should be recalculated on save",
        )

