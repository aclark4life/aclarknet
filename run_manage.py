#!/usr/bin/env python
"""Helper script to run manage.py commands with xhtml2pdf mocked."""
import sys
from unittest.mock import MagicMock

# Mock xhtml2pdf before any imports
sys.modules['xhtml2pdf'] = MagicMock()
sys.modules['xhtml2pdf.pisa'] = MagicMock()
sys.modules['xhtml2pdf'].pisa = MagicMock()

# Now run manage.py
if __name__ == "__main__":
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aclarknet.settings.dev")
    
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
