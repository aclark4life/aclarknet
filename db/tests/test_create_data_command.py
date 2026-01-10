"""Tests for create_data management command."""

from decimal import Decimal
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from db.models import Task, Invoice, Time, User, Client, Project


class CreateDataCommandTest(TestCase):
    """Test that create_data command generates real invoice data."""

    def test_task_rate_is_100(self):
        """Test that tasks are created with rate=$100."""
        # Run the command with minimal data
        call_command('create_data', '--companies=1', '--clients=1', '--projects=2', 
                     '--invoices=1', '--times=1', '--users=1', stdout=StringIO())
        
        # Check that tasks have rate=$100
        tasks = Task.objects.exclude(name="Default Task")
        self.assertTrue(tasks.exists())
        for task in tasks:
            self.assertEqual(task.rate, Decimal('100'))

    def test_time_amount_calculated_from_rate_and_hours(self):
        """Test that time entry amounts are calculated from rate * hours."""
        # Run the command with minimal data
        call_command('create_data', '--companies=1', '--clients=1', '--projects=2', 
                     '--invoices=1', '--times=5', '--users=1', stdout=StringIO())
        
        # Check that time entries have calculated amounts
        time_entries = Time.objects.all()
        for time_entry in time_entries:
            if time_entry.task and time_entry.task.rate:
                expected_amount = time_entry.task.rate * time_entry.hours
                self.assertEqual(time_entry.amount, expected_amount,
                               f"Time entry {time_entry.id}: expected {expected_amount}, got {time_entry.amount}")

    def test_invoice_amount_calculated_from_time_entries(self):
        """Test that invoice amounts are calculated from sum of time entries."""
        # Run the command with minimal data
        call_command('create_data', '--companies=1', '--clients=1', '--projects=2', 
                     '--invoices=2', '--times=10', '--users=1', stdout=StringIO())
        
        # Check that invoice amounts match sum of their time entries
        invoices = Invoice.objects.all()
        for invoice in invoices:
            time_entries = Time.objects.filter(invoice=invoice)
            expected_amount = sum((time.amount or Decimal('0')) for time in time_entries)
            self.assertEqual(invoice.amount, expected_amount,
                           f"Invoice {invoice.id}: expected {expected_amount}, got {invoice.amount}")

    def test_invoice_paid_amount_is_portion_of_total(self):
        """Test that invoice paid_amount is between 0 and the total amount."""
        # Run the command with minimal data
        call_command('create_data', '--companies=1', '--clients=1', '--projects=2', 
                     '--invoices=3', '--times=15', '--users=1', stdout=StringIO())
        
        # Check that paid amounts are reasonable
        invoices = Invoice.objects.all()
        for invoice in invoices:
            if invoice.amount > 0:
                self.assertGreaterEqual(invoice.paid_amount, Decimal('0'))
                self.assertLessEqual(invoice.paid_amount, invoice.amount)

    def test_default_task_rate_is_100(self):
        """Test that the default task is created with rate=$100."""
        # Get or create the default task
        default_task = Task.get_default_task()
        
        # Check that it has rate=$100
        self.assertEqual(default_task.name, "Default Task")
        self.assertEqual(default_task.rate, Decimal('100'))
        self.assertEqual(default_task.unit, Decimal('1.0'))
