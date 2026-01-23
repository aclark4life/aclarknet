#!/usr/bin/env python
"""
dm - Django Management wrapper

A convenience CLI wrapper around Django management commands.
Provides a shorter syntax for common Django management tasks.

Usage:
    dm repo sync              # Sync repository with upstream
    dm repo sync --upstream origin --branch main
"""

import os
import sys


def main():
    """Main entry point for the dm CLI."""
    # Set Django settings module if not already set
    # Allows users to override with DJANGO_SETTINGS_MODULE env var
    if "DJANGO_SETTINGS_MODULE" not in os.environ:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aclarknet.settings.dev")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Transform dm commands to Django management commands
    # dm repo sync -> python manage.py repo sync
    if len(sys.argv) > 1:
        # Insert 'manage.py' as argv[0] for Django's command system
        sys.argv[0] = "manage.py"

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
