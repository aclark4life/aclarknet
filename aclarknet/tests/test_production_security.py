"""
Tests to ensure production security settings are properly configured.
"""
import os
from unittest import TestCase
from unittest.mock import patch


class ProductionSecurityTestCase(TestCase):
    """Test that production settings are secure."""

    @patch.dict(os.environ, {
        'DJANGO_SECRET_KEY': 'test-secret-key-for-testing-only',
        'DJANGO_ALLOWED_HOSTS': 'example.com'
    })
    def test_hijack_not_in_production(self):
        """Test that django-hijack is not enabled in production settings."""
        # Import production settings with mocked environment
        from aclarknet.settings import production
        
        # Verify DEBUG is False in production
        self.assertFalse(production.DEBUG)
        
        # Verify hijack is NOT in INSTALLED_APPS
        self.assertNotIn('hijack', production.INSTALLED_APPS)
        self.assertNotIn('hijack.contrib.admin', production.INSTALLED_APPS)
        
        # Verify hijack middleware is NOT in MIDDLEWARE
        hijack_middleware = 'hijack.middleware.HijackUserMiddleware'
        self.assertNotIn(hijack_middleware, production.MIDDLEWARE)
