"""Test settings for aclarknet project - uses mongomock for testing."""
import sys
from unittest.mock import MagicMock

# Mock xhtml2pdf before importing anything else
sys.modules['xhtml2pdf'] = MagicMock()
sys.modules['xhtml2pdf.pisa'] = MagicMock()

from aclarknet.settings.dev import *  # noqa: F401, F403

# Override database to use mongomock for testing
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "NAME": "test_aclarknet",
        "CLIENT": {
            "connect": False,
        },
        "ENFORCE_SCHEMA_VALIDATION": False,
    }
}

# Monkey-patch pymongo to use mongomock
import mongomock
import sys
sys.modules['pymongo'] = mongomock
from pymongo.mongo_client import MongoClient as OriginalMongoClient
import pymongo
pymongo.MongoClient = mongomock.MongoClient
pymongo.DESCENDING = -1
pymongo.ASCENDING = 1

# Also patch the django_mongodb_backend connection
import django_mongodb_backend.base
original_get_new_connection = django_mongodb_backend.base.DatabaseCreation.get_new_connection

def get_new_connection_with_mongomock(self):
    """Use mongomock for testing."""
    return mongomock.MongoClient(tz_aware=True)

django_mongodb_backend.base.DatabaseCreation.get_new_connection = get_new_connection_with_mongomock
