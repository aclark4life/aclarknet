"""Tests for the update_selected_entries bulk action view."""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from db.models import Invoice, Task
from siteuser.models import SiteUser


class UpdateSelectedEntriesMarkPaidTests(TestCase):
    """Test the bulk 'mark_paid' action used by the invoice index page."""

    def setUp(self):
        self.superuser = SiteUser.objects.create_superuser(
            username="admin-bulk-mark-paid-test", password="testpass123"
        )
        self.client.force_login(self.superuser)

    def test_mark_paid_sets_paid_amount_for_selected_invoices(self):
        invoice1 = Invoice.objects.create(
            name="Bulk Paid 1", amount=Decimal("100.00")
        )
        invoice2 = Invoice.objects.create(
            name="Bulk Paid 2", amount=Decimal("200.00")
        )

        url = reverse("update-selected")
        response = self.client.post(
            url,
            {
                "model_name": "invoice",
                "action": "mark_paid",
                "entry_id": [str(invoice1.pk), str(invoice2.pk)],
            },
        )

        self.assertEqual(response.status_code, 302)
        invoice1.refresh_from_db()
        invoice2.refresh_from_db()
        self.assertEqual(invoice1.paid_amount, invoice1.amount)
        self.assertEqual(invoice2.paid_amount, invoice2.amount)
        self.assertEqual(invoice1.balance, 0)
        self.assertEqual(invoice2.balance, 0)

    def test_mark_paid_rejected_for_non_invoice_models(self):
        task = Task.objects.create(name="Some Task")

        url = reverse("update-selected")
        response = self.client.post(
            url,
            {
                "model_name": "task",
                "action": "mark_paid",
                "entry_id": [str(task.pk)],
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())
