"""
Tests to ensure production security settings are properly configured.
"""
import os
import sys
from unittest import TestCase
from pathlib import Path


class ProductionSecurityTestCase(TestCase):
    """Test that production settings are secure."""

    def test_hijack_not_in_production(self):
        """Test that django-hijack is not enabled in production settings."""
        # Import production settings module
        project_dir = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(project_dir))
        
        # Set required environment variables for production settings
        os.environ['DJANGO_SECRET_KEY'] = 'test-secret-key-for-testing-only'
        os.environ['DJANGO_ALLOWED_HOSTS'] = 'example.com'
        
        # Import production settings
        from aclarknet.settings import production
        
        # Verify DEBUG is False in production
        self.assertFalse(production.DEBUG)
        
        # Verify hijack is NOT in INSTALLED_APPS
        self.assertNotIn('hijack', production.INSTALLED_APPS)
        self.assertNotIn('hijack.contrib.admin', production.INSTALLED_APPS)
        
        # Verify hijack middleware is NOT in MIDDLEWARE
        hijack_middleware = 'hijack.middleware.HijackUserMiddleware'
        self.assertNotIn(hijack_middleware, production.MIDDLEWARE)
