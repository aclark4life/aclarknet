# Related Fields Configuration Refactoring

## Overview

This document describes the refactoring of field name handling in the `related.html` template and view classes to improve maintainability and flexibility.

## Problem Statement

Previously, the `related.html` template had hardcoded field names in two places:
1. Line 20: Hardcoded title fields (`name`, `title`, `subject`, `description`)
2. Line 27: Hardcoded excluded fields (`type`, `id`, `item`, `name`, `title`, `subject`, `description`)

This created tight coupling between the template and business logic, making it difficult to:
- Customize which fields appear in related items for specific views
- Maintain consistent field display rules across the application
- Understand the field filtering logic without reading both view and template code

## Solution

### 1. BaseView Configuration Attributes

Added two new class attributes to `BaseView` (in `db/views/base.py`):

```python
# ---- Related items display customization ----
# These control how related items are displayed in related.html template
related_title_fields = ["name", "title", "subject", "description"]  # Fields shown in card title
related_excluded_fields = ["type", "id", "item"]  # Fields never shown in related cards
```

### 2. Context Data Passing

Modified `get_context_data()` in `BaseView` to pass these configurations to the template:

```python
if self.has_related and self.queryset_related is not None:
    context["has_related"] = True
    context["related_title_fields"] = self.related_title_fields
    context["related_excluded_fields"] = self.related_excluded_fields
    queryset = self.queryset_related
    related = True
```

### 3. Template Simplification

Updated `related.html` to use the view configuration instead of hardcoded values:

**Before:**
```django
{% if field_name == "name" or field_name == "title" or field_name == "subject" or field_name == "description" %}
```

**After:**
```django
{% if field_name in related_title_fields %}
```

**Before:**
```django
{% if field_name != "type" and field_name != "id" and field_name != "item" and field_name != "name" and field_name != "title" and field_name != "subject" and field_name != "description" and field_value %}
```

**After:**
```django
{% if field_name not in related_excluded_fields and field_name not in related_title_fields and field_value %}
```

## Benefits

1. **Maintainability**: Field display rules are centralized in view classes rather than scattered in templates
2. **Flexibility**: Subclasses can override `related_title_fields` and `related_excluded_fields` per view
3. **Consistency**: Same pattern as existing `field_values_include/exclude` attributes in BaseView
4. **Simplicity**: Template logic reduced from 9 explicit field checks to simple list membership tests
5. **Reusability**: Template can be reused with different field configurations

## Usage Examples

### Using Default Configuration

```python
class ClientDetailView(BaseClientView, DetailView):
    """Uses default related field configuration from BaseView."""
    template_name = "view.html"
    # Will use default:
    # - related_title_fields = ["name", "title", "subject", "description"]
    # - related_excluded_fields = ["type", "id", "item"]
```

### Custom Configuration

```python
class InvoiceDetailView(BaseInvoiceView, DetailView):
    """Custom related field configuration."""
    template_name = "view.html"
    
    # Override to show only 'subject' in title
    related_title_fields = ["subject"]
    
    # Override to exclude additional fields
    related_excluded_fields = ["type", "id", "item", "internal_notes"]
```

## Testing

New tests were added in `db/tests/test_related_fields_config.py`:
- Test default configuration values
- Test custom configuration in subclasses
- Test that configuration is passed to template context
- Test that configuration is only added when `has_related=True`

## Backwards Compatibility

This refactoring maintains 100% backwards compatibility:
- All existing views use the default configuration, which matches the previous hardcoded values
- The template behavior is identical for views that don't override the configuration
- No changes are required to existing view classes

## Future Enhancements

Potential future improvements:
1. Add `related_display_order` to control field ordering in related items
2. Add `related_primary_field` to specify a single field for simplified display
3. Create a `@property` decorator to compute configurations dynamically
4. Add template tag filters for more complex field filtering logic
