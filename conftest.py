"""Pytest configuration to mock unavailable modules."""
import sys
from unittest.mock import MagicMock

# Mock xhtml2pdf and its pisa module before any imports
sys.modules['xhtml2pdf'] = MagicMock()
sys.modules['xhtml2pdf.pisa'] = MagicMock()

# Also mock pisa directly
sys.modules['xhtml2pdf'].pisa = MagicMock()
