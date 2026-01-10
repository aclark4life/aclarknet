# Field Values Refactoring

## Overview

The `field_values` mechanism in template context has been refactored to provide better defaults and easier customization for both detail views and list/index views.

## Changes

### Before

- Detail views only showed fields if user was a superuser
- List views only showed hardcoded attributes: `type`, `id`, `amount`, `cost`, `net`, `hours`
- Views had to manually append to `context['field_values']` after calling `super().get_context_data()`
- No easy way to customize which fields to show

### After

- **All form fields are shown by default** in both detail views and list views
- Views can easily customize field display using class attributes
- Same customization options work for both detail views and list/index views
- Cleaner, more maintainable code

## Usage

### Detail Views

#### Default Behavior

By default, all fields from `form_class` are displayed in detail views:

```python
class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"
    # All fields from ClientForm will be shown automatically
```

#### Customization Options

##### 1. Include Only Specific Fields

Show only specific fields:

```python
class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"
    field_values_include = ["name", "url"]  # Only show these fields
```

##### 2. Exclude Specific Fields

Show all fields except some:

```python
class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"
    field_values_exclude = ["internal_notes", "secret_field"]  # Hide these
```

##### 3. Add Extra Computed Fields

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

##### 4. Combined Customization

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

### List/Index Views

The same customization options now work for list views (index views)!

#### Default Behavior

By default, all fields from `form_class` are displayed in list views:

```python
class ClientListView(BaseClientView, ListView):
    template_name = "index.html"
    # All fields from ClientForm will be shown automatically
```

#### Customization Options for List Views

##### 1. Include Only Specific Fields

Show only specific columns in the table:

```python
class ClientListView(BaseClientView, ListView):
    template_name = "index.html"
    field_values_include = ["name", "url"]  # Only show these columns
```

##### 2. Exclude Specific Fields

Show all fields except some:

```python
class InvoiceListView(BaseInvoiceView, ListView):
    template_name = "index.html"
    field_values_exclude = ["description", "notes"]  # Hide these columns
```

##### 3. Add Extra Computed Fields

Add additional computed columns:

```python
class InvoiceListView(BaseInvoiceView, ListView):
    template_name = "index.html"
    
    def get_context_data(self, **kwargs):
        # Add a status column to all rows
        self.field_values_extra = [
            ("Status", "Active"),
        ]
        return super().get_context_data(**kwargs)
```

##### 4. Combined Customization for List Views

```python
class InvoiceListView(BaseInvoiceView, ListView):
    template_name = "index.html"
    field_values_include = ["subject", "amount", "due_date"]
    
    def get_context_data(self, **kwargs):
        self.field_values_extra = [
            ("Status", "Pending"),
        ]
        return super().get_context_data(**kwargs)
```

## Implementation Details

### BaseView Class Attributes

```python
class BaseView:
    # Field values customization (works for both detail and list views)
    field_values_include = None  # List of field names to include (None = all fields)
    field_values_exclude = None  # List of field names to exclude
    field_values_extra = None    # List of (field_name, value) tuples to append
```

### get_field_values() Method

The refactored method works for both detail and list views:

**For Detail Views (no page_obj):**
1. Gets all fields from `form_class`
2. Applies `field_values_include` filter (if set)
3. Applies `field_values_exclude` filter (if set)
4. Builds list of (field_name, value) tuples
5. Appends `field_values_extra` items (if set)
6. Returns the complete list

**For List Views (with page_obj):**
1. Gets all fields from `form_class`
2. Applies `field_values_include` filter (if set)
3. Applies `field_values_exclude` filter (if set)
4. For each item in page_obj:
   - Adds `type` and `id` fields
   - Adds all form fields that exist on the item
   - Appends `field_values_extra` items (if set)
5. Returns list of field values for each item

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

- Existing views without customization will now show all form fields (instead of hardcoded attributes)
- The template variable `field_values` (detail) and `field_values_page` (list) still work the same way
- Views without `form_class` fall back to hardcoded attributes: `amount`, `cost`, `net`, `hours`

## Testing

Tests are available in `db/tests/test_field_values.py` covering:

**Detail Views:**
- Default behavior (all fields)
- Include filter
- Exclude filter  
- Extra fields
- Combined customization

**List Views:**
- Default behavior (all form fields)
- Include filter
- Exclude filter
- Extra fields
- Backward compatibility
