"""Tests for client categorization feature."""

from django.test import TestCase

from db.models import Client


class ClientCategorizationTest(TestCase):
    """Test client categorization and featuring functionality."""

    def setUp(self):
        """Set up test data."""
        # Create featured clients with categories
        self.gov_client = Client.objects.create(
            name="Government Agency",
            featured=True,
            category=Client.ClientCategory.GOVERNMENT,
        )
        self.nonprofit_client = Client.objects.create(
            name="Non-profit Organization",
            featured=True,
            category=Client.ClientCategory.NONPROFIT,
        )
        self.private_client = Client.objects.create(
            name="Private Company",
            featured=True,
            category=Client.ClientCategory.PRIVATE,
        )
        # Create non-featured client
        self.hidden_client = Client.objects.create(
            name="Hidden Client", featured=False, category=Client.ClientCategory.PRIVATE
        )

    def test_client_featured_field_default(self):
        """Test that featured field defaults to False."""
        client = Client.objects.create(name="New Client")
        self.assertFalse(client.featured)

    def test_client_category_choices(self):
        """Test that category choices are available."""
        self.assertEqual(self.gov_client.category, "government")
        self.assertEqual(self.nonprofit_client.category, "non-profit")
        self.assertEqual(self.private_client.category, "private")

    def test_client_category_display(self):
        """Test that category display names work correctly."""
        self.assertEqual(self.gov_client.get_category_display(), "Government")
        self.assertEqual(self.nonprofit_client.get_category_display(), "Non-Profit")
        self.assertEqual(self.private_client.get_category_display(), "Private Sector")

    def test_featured_clients_filter(self):
        """Test filtering for featured clients."""
        featured_clients = Client.objects.filter(featured=True)
        self.assertEqual(featured_clients.count(), 3)
        self.assertIn(self.gov_client, featured_clients)
        self.assertIn(self.nonprofit_client, featured_clients)
        self.assertIn(self.private_client, featured_clients)
        self.assertNotIn(self.hidden_client, featured_clients)

    def test_clients_grouped_by_category(self):
        """Test grouping clients by category."""
        from collections import defaultdict

        featured_clients = Client.objects.filter(featured=True).order_by(
            "category", "name"
        )
        categories = defaultdict(list)
        for client in featured_clients:
            category_display = (
                client.get_category_display() if client.category else "Other"
            )
            categories[category_display].append(client)

        self.assertIn("Government", categories)
        self.assertIn("Non-Profit", categories)
        self.assertIn("Private Sector", categories)
        self.assertEqual(len(categories["Government"]), 1)
        self.assertEqual(len(categories["Non-Profit"]), 1)
        self.assertEqual(len(categories["Private Sector"]), 1)


class ClientsViewTest(TestCase):
    """Test the clients view with categorization."""

    def setUp(self):
        """Set up test data."""
        # Create some featured clients
        Client.objects.create(
            name="Gov Client 1",
            featured=True,
            category=Client.ClientCategory.GOVERNMENT,
        )
        Client.objects.create(
            name="Gov Client 2",
            featured=True,
            category=Client.ClientCategory.GOVERNMENT,
        )
        Client.objects.create(
            name="NonProfit Client",
            featured=True,
            category=Client.ClientCategory.NONPROFIT,
        )
        # Non-featured client
        Client.objects.create(name="Hidden Client", featured=False)

    def test_clients_view_displays_featured_only(self):
        """Test that the clients view only displays featured clients."""
        from cms.views import ClientsView

        view = ClientsView()
        context = view.get_context_data()

        self.assertIn("categories", context)
        categories = context["categories"]

        # Count total clients displayed
        total_displayed = sum(len(clients) for clients in categories.values())
        self.assertEqual(total_displayed, 3)  # Only featured clients

    def test_clients_view_groups_by_category(self):
        """Test that the clients view groups clients by category."""
        from cms.views import ClientsView

        view = ClientsView()
        context = view.get_context_data()

        categories = context["categories"]
        self.assertIn("Government", categories)
        self.assertIn("Non-Profit", categories)
        self.assertEqual(len(categories["Government"]), 2)
        self.assertEqual(len(categories["Non-Profit"]), 1)
