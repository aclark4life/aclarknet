"""Context processors for aclarknet templates."""

from django.conf import settings


def analytics(request):
    """Expose the Google Analytics measurement ID to all templates."""
    return {"GA_MEASUREMENT_ID": getattr(settings, "GA_MEASUREMENT_ID", "")}
