"""Utility functions for the db app."""

import locale

from django import apps


def get_model_class(model_name, app_label="db"):
    """
    Get a Django model class by name.

    Args:
        model_name: Name of the model (will be capitalized)
        app_label: App label (default: "db")

    Returns:
        Django model class
    """
    return apps.get_model(app_label=app_label, model_name=model_name.capitalize())


# Set locale for currency formatting
locale.setlocale(locale.LC_ALL, "")
