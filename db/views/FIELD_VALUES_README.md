# Field Values Refactoring

## Overview

The `field_values` mechanism in template context has been refactored to provide better defaults and easier customization.

## Changes

### Before

- Detail views only showed fields if user was a superuser
- Views had to manually append to `context['field_values']` after calling `super().get_context_data()`
- No easy way to customize which fields to show

### After

- **All form fields are shown by default** in detail views
- Views can easily customize field display using class attributes
- Cleaner, more maintainable code

## Usage

### Default Behavior

By default, all fields from `form_class` are displayed in detail views:

```python
class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"
    # All fields from ClientForm will be shown automatically
```

### Customization Options

#### 1. Include Only Specific Fields

Show only specific fields:

```python
class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"
    field_values_include = ["name", "url"]  # Only show these fields
```

#### 2. Exclude Specific Fields

Show all fields except some:

```python
class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"
    field_values_exclude = ["internal_notes", "secret_field"]  # Hide these
```

#### 3. Add Extra Computed Fields

Add additional fields with computed/formatted values:

```python
class InvoiceDetailView(BaseInvoiceView, DetailView):
    template_name = "view.html"
    
    def get_context_data(self, **kwargs):
        invoice = self.get_object()
        
        # Set extra fields with formatted values
        self.field_values_extra = [
            ("Total", locale.currency(invoice.amount, grouping=True)),
            ("Cost", locale.currency(invoice.cost, grouping=True)),
            ("Net", locale.currency(invoice.net, grouping=True)),
            ("Hours", invoice.hours),
        ]
        
        return super().get_context_data(**kwargs)
```

#### 4. Combined Customization

You can combine multiple customization options:

```python
class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"
    field_values_include = ["name", "email", "phone"]
    
    def get_context_data(self, **kwargs):
        client = self.get_object()
        self.field_values_extra = [
            ("Projects Count", client.project_set.count()),
            ("Total Revenue", calculate_revenue(client)),
        ]
        return super().get_context_data(**kwargs)
```

## Implementation Details

### BaseView Class Attributes

```python
class BaseView:
    # Field values customization
    field_values_include = None  # List of field names to include (None = all fields)
    field_values_exclude = None  # List of field names to exclude
    field_values_extra = None    # List of (field_name, value) tuples to append
```

### get_field_values() Method

The refactored method:

1. Gets all fields from `form_class`
2. Applies `field_values_include` filter (if set)
3. Applies `field_values_exclude` filter (if set)
4. Builds list of (field_name, value) tuples
5. Appends `field_values_extra` items (if set)
6. Returns the complete list

## Migration Guide

### Old Pattern

```python
class InvoiceDetailView(BaseInvoiceView, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Manually append after context is created
        context["field_values"].append(("Total", formatted_total))
        context["field_values"].append(("Cost", formatted_cost))
        return context
```

### New Pattern

```python
class InvoiceDetailView(BaseInvoiceView, DetailView):
    def get_context_data(self, **kwargs):
        # Set field_values_extra BEFORE calling super()
        self.field_values_extra = [
            ("Total", formatted_total),
            ("Cost", formatted_cost),
        ]
        return super().get_context_data(**kwargs)
```

## Backward Compatibility

- List views (with `page_obj`) work exactly as before
- Existing views without customization will now show all fields (previously required superuser)
- The template variable `field_values` still works the same way

## Testing

Tests are available in `db/tests/test_field_values.py` covering:
- Default behavior (all fields)
- Include filter
- Exclude filter  
- Extra fields
- Combined customization
- List view compatibility
