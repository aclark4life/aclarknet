# Faker Integration for Create Views

This feature automatically populates create forms with fake/sample data when the application is running in DEBUG mode. This makes it easier and faster to test the application without having to manually enter data for every field.

## How It Works

### 1. faker_utils.py
Contains utility functions that generate fake data for each model type:
- `get_fake_client_data()` - Generates fake client data
- `get_fake_company_data()` - Generates fake company data
- `get_fake_contact_data()` - Generates fake contact data
- `get_fake_project_data()` - Generates fake project data
- `get_fake_task_data()` - Generates fake task data
- `get_fake_invoice_data()` - Generates fake invoice data
- `get_fake_time_data()` - Generates fake time entry data
- `get_fake_note_data()` - Generates fake note data

All functions check if DEBUG mode is enabled and if Faker is available before generating data. If either condition is false, they return an empty dictionary.

### 2. FakeDataMixin
A reusable mixin in `db/views/base.py` that:
- Adds fake data to form initial values
- Only activates when `settings.DEBUG` is `True`
- Only works if Faker library is installed
- Respects existing initial values (doesn't override them)
- Gracefully handles missing Faker library

### 3. Usage in Views
Each CreateView class inherits from `FakeDataMixin` and specifies which faker function to use:

```python
class ClientCreateView(FakeDataMixin, BaseClientView, CreateView):
    template_name = "edit.html"
    fake_data_function = 'get_fake_client_data'
```

## Benefits

1. **DRY (Don't Repeat Yourself)**: Fake data generation logic is centralized in `faker_utils.py`
2. **Safe**: Only activates in DEBUG mode
3. **Non-intrusive**: Doesn't override existing initial values
4. **Maintainable**: Each model has its own faker function, making it easy to update
5. **Testable**: Comprehensive test coverage ensures the feature works correctly

## Testing

Run the tests with:
```bash
pytest db/tests/test_faker_utils.py
pytest db/tests/test_fake_data_mixin.py
```

## Development Workflow

When creating a new object in DEBUG mode:
1. Navigate to a create form (e.g., `/client/create/`)
2. The form will be pre-populated with fake data
3. You can modify any field or just save as-is
4. This saves time during development and testing

## Production Behavior

In production (when `DEBUG=False`):
- No fake data is generated
- Forms behave normally with empty fields or programmatically set initial values
- Zero performance impact since faker imports are skipped
