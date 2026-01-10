"""Utility functions for the db app."""

import locale

from django import apps
from django.db.models import BooleanField, Case, Value, When


def get_archived_annotation():
    """Return a Case annotation for checking if a user is archived."""
    return Case(
        When(is_active=False, then=Value(True)),
        default=Value(False),
        output_field=BooleanField(),
    )


def get_queryset(model_class, filter_by=None, order_by=None):
    """
    Get a queryset for a model with optional filtering and ordering.

    Args:
        model_class: Django model class
        filter_by: Dictionary of filter parameters
        order_by: List of ordering fields

    Returns:
        Dictionary with 'queryset' key containing the filtered/ordered queryset
    """
    result = {}
    queryset = model_class.objects.all()

    if filter_by:
        queryset = queryset.filter(**filter_by)

    if order_by:
        queryset = queryset.order_by(*order_by)

    result["queryset"] = queryset
    return result


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
