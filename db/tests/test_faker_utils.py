"""Tests for faker_utils module."""

from django.conf import settings
from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock

from db.faker_utils import (
    get_faker,
    get_fake_client_data,
    get_fake_company_data,
    get_fake_contact_data,
    get_fake_project_data,
    get_fake_task_data,
    get_fake_invoice_data,
    get_fake_time_data,
    get_fake_note_data,
)


class GetFakerTest(TestCase):
    """Tests for get_faker function."""

    @override_settings(DEBUG=False)
    def test_get_faker_returns_none_when_not_debug(self):
        """get_faker should return None when DEBUG is False."""
        result = get_faker()
        self.assertIsNone(result)

    @override_settings(DEBUG=True)
    def test_get_faker_returns_faker_when_debug(self):
        """get_faker should return Faker instance when DEBUG is True."""
        result = get_faker()
        self.assertIsNotNone(result)
        # Check that it's a Faker instance by verifying it has common methods
        self.assertTrue(hasattr(result, 'name'))
        self.assertTrue(hasattr(result, 'email'))

    @override_settings(DEBUG=True)
    @patch('db.faker_utils.Faker', side_effect=ImportError)
    def test_get_faker_returns_none_when_import_error(self, mock_faker):
        """get_faker should return None when Faker import fails."""
        result = get_faker()
        self.assertIsNone(result)


class FakeDataFunctionsTest(TestCase):
    """Tests for fake data generation functions."""

    @override_settings(DEBUG=False)
    def test_fake_data_functions_return_empty_dict_when_not_debug(self):
        """All fake data functions should return empty dict when DEBUG is False."""
        functions = [
            get_fake_client_data,
            get_fake_company_data,
            get_fake_contact_data,
            get_fake_project_data,
            get_fake_task_data,
            get_fake_invoice_data,
            get_fake_time_data,
            get_fake_note_data,
        ]
        
        for func in functions:
            with self.subTest(function=func.__name__):
                result = func()
                self.assertEqual(result, {})

    @override_settings(DEBUG=True)
    def test_get_fake_client_data_returns_valid_data(self):
        """get_fake_client_data should return dict with expected keys."""
        result = get_fake_client_data()
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
        self.assertIn('description', result)
        self.assertIn('url', result)
        # Verify values are not empty
        self.assertTrue(result['name'])
        self.assertTrue(result['description'])
        self.assertTrue(result['url'])

    @override_settings(DEBUG=True)
    def test_get_fake_company_data_returns_valid_data(self):
        """get_fake_company_data should return dict with expected keys."""
        result = get_fake_company_data()
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
        self.assertIn('description', result)
        self.assertIn('url', result)

    @override_settings(DEBUG=True)
    def test_get_fake_contact_data_returns_valid_data(self):
        """get_fake_contact_data should return dict with expected keys."""
        result = get_fake_contact_data()
        self.assertIsInstance(result, dict)
        self.assertIn('first_name', result)
        self.assertIn('last_name', result)
        self.assertIn('email', result)
        self.assertIn('number', result)
        self.assertIn('url', result)

    @override_settings(DEBUG=True)
    def test_get_fake_project_data_returns_valid_data(self):
        """get_fake_project_data should return dict with expected keys."""
        result = get_fake_project_data()
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
        self.assertIn('description', result)

    @override_settings(DEBUG=True)
    def test_get_fake_task_data_returns_valid_data(self):
        """get_fake_task_data should return dict with expected keys."""
        result = get_fake_task_data()
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
        self.assertIn('rate', result)
        self.assertIn('unit', result)
        # Verify rate is a reasonable number
        self.assertGreaterEqual(result['rate'], 50)
        self.assertLessEqual(result['rate'], 200)

    @override_settings(DEBUG=True)
    def test_get_fake_invoice_data_returns_valid_data(self):
        """get_fake_invoice_data should return dict with expected keys."""
        result = get_fake_invoice_data()
        self.assertIsInstance(result, dict)
        self.assertIn('subject', result)

    @override_settings(DEBUG=True)
    def test_get_fake_time_data_returns_valid_data(self):
        """get_fake_time_data should return dict with expected keys."""
        result = get_fake_time_data()
        self.assertIsInstance(result, dict)
        self.assertIn('description', result)
        self.assertIn('hours', result)
        # Verify hours is a reasonable number
        self.assertGreaterEqual(result['hours'], 1)
        self.assertLessEqual(result['hours'], 8)

    @override_settings(DEBUG=True)
    def test_get_fake_note_data_returns_valid_data(self):
        """get_fake_note_data should return dict with expected keys."""
        result = get_fake_note_data()
        self.assertIsInstance(result, dict)
        self.assertIn('title', result)
        self.assertIn('text', result)
