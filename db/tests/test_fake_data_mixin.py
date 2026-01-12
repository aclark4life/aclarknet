"""Tests for FakeDataMixin."""

from django.test import TestCase, override_settings, RequestFactory
from django.views.generic import CreateView
from unittest.mock import patch

from db.models import Client
from db.forms import ClientForm
from db.views.base import FakeDataMixin


class FakeDataMixinTestView(FakeDataMixin, CreateView):
    """Test view using FakeDataMixin."""
    model = Client
    form_class = ClientForm
    fake_data_function = 'get_fake_client_data'


class FakeDataMixinTest(TestCase):
    """Tests for FakeDataMixin."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = RequestFactory()
        self.request = self.factory.get('/test/')
        self.view = FakeDataMixinTestView()
        self.view.request = self.request

    @override_settings(DEBUG=False)
    def test_get_initial_does_not_add_fake_data_when_not_debug(self):
        """get_initial should not add fake data when DEBUG is False."""
        initial = self.view.get_initial()
        # Should be empty or minimal - no fake data
        self.assertNotIn('name', initial)
        self.assertNotIn('description', initial)

    @override_settings(DEBUG=True)
    def test_get_initial_adds_fake_data_when_debug(self):
        """get_initial should add fake data when DEBUG is True."""
        initial = self.view.get_initial()
        # Should have fake data
        self.assertIn('name', initial)
        self.assertIn('description', initial)
        self.assertIn('url', initial)
        # Verify values are not empty
        self.assertTrue(initial['name'])
        self.assertTrue(initial['description'])
        self.assertTrue(initial['url'])

    @override_settings(DEBUG=True)
    def test_get_initial_preserves_existing_values(self):
        """get_initial should not override existing initial values."""
        # Create a view with existing initial data
        class ViewWithInitial(FakeDataMixinTestView):
            def get_initial(self):
                initial = super(CreateView, self).get_initial()
                initial['name'] = 'Existing Name'
                initial = super().get_initial()  # Call mixin's get_initial
                return initial
        
        view = ViewWithInitial()
        view.request = self.request
        initial = view.get_initial()
        
        # The existing name should be preserved
        self.assertEqual(initial['name'], 'Existing Name')
        # But other fields should have fake data
        self.assertIn('description', initial)
        self.assertTrue(initial['description'])

    @override_settings(DEBUG=True)
    def test_view_without_fake_data_function_doesnt_add_data(self):
        """Views without fake_data_function should not add fake data."""
        class ViewWithoutFunction(FakeDataMixin, CreateView):
            model = Client
            form_class = ClientForm
            # No fake_data_function set
        
        view = ViewWithoutFunction()
        view.request = self.request
        initial = view.get_initial()
        
        # Should not have fake data
        self.assertNotIn('name', initial)

    @override_settings(DEBUG=True)
    def test_invalid_function_name_does_not_raise_error(self):
        """Invalid fake_data_function should not raise an error."""
        class ViewWithInvalidFunction(FakeDataMixin, CreateView):
            model = Client
            form_class = ClientForm
            fake_data_function = 'nonexistent_function'
        
        view = ViewWithInvalidFunction()
        view.request = self.request
        
        # Should not raise an error
        initial = view.get_initial()
        self.assertIsInstance(initial, dict)
