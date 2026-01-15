"""Custom template filters for text formatting."""
from django import template

register = template.Library()


@register.filter
def title_case(value):
    """Convert snake_case or any text to Title Case.
    
    Examples:
        'first_name' -> 'First Name'
        'start_date' -> 'Start Date'
        'url' -> 'Url'
        'is_active' -> 'Is Active'
    """
    if not value:
        return value
    
    # Replace underscores with spaces and capitalize each word
    return value.replace('_', ' ').title()
