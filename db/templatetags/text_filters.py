"""Custom template filters for text formatting."""
from django import template

register = template.Library()


@register.filter
def title_case(value):
    """Convert snake_case or any text to Title Case.
    
    Replaces underscores with spaces and capitalizes each word.
    
    Args:
        value (str): The string to convert (typically a field name).
        
    Returns:
        str: The converted string in Title Case, or the original value if None/empty.
    
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
