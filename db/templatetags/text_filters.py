"""Custom template filters for text formatting."""

from django import template
from db.templatetags.babel import currencyfmt

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
    return value.replace("_", " ").title()


@register.filter
def format_field_value(field_value, field_name):
    """Format field value based on field name.

    Automatically formats currency fields (amount, paid_amount, cost, net, balance)
    with USD currency formatting. Invoice fields show the invoice name or "Not invoiced".
    Other fields get default formatting.

    Args:
        field_value: The value to format.
        field_name (str): The name of the field (used to determine formatting).

    Returns:
        Formatted field value. Currency fields return a string with formatting,
        hours field returns int/float, invoice field returns invoice name or "Not invoiced",
        other fields return the value as-is or empty string.

    Examples:
        {{ field_value|format_field_value:field_name }}
        {{ 100.50|format_field_value:"amount" }} -> "$100.50"
        {{ 25|format_field_value:"hours" }} -> "25"
        {{ invoice_obj|format_field_value:"invoice" }} -> "INV-2024-01-15-123"
        {{ None|format_field_value:"invoice" }} -> "Not invoiced"
        {{ "Test"|format_field_value:"name" }} -> "Test"
    """
    # List of field names that should be formatted as currency
    currency_fields = ["amount", "paid_amount", "cost", "net", "balance"]

    if field_name in currency_fields:
        # Format as USD currency, default to 0 if value is None/empty
        value = field_value if field_value is not None else 0
        return currencyfmt(value, "USD")
    elif field_name == "hours":
        # For hours, default to 0 if None
        return field_value if field_value is not None else 0
    elif field_name == "invoice":
        # For invoice field, show invoice name or "Not invoiced"
        if field_value is None:
            return "Not invoiced"
        # If it's an Invoice object, convert to string (uses __str__ method)
        return str(field_value)
    else:
        # For all other fields, default to empty string if None
        return field_value if field_value is not None else ""
