# Faker Integration Examples

## Example 1: Creating a Client (DEBUG=True)

### Before (without faker integration):
```
Visit: http://localhost:8000/client/create/

Form fields are empty:
┌─────────────────────────────────────┐
│ Name:         [                  ]  │
│ Description:  [                  ]  │
│ URL:          [                  ]  │
│                                     │
│         [Submit]  [Cancel]          │
└─────────────────────────────────────┘

User must type everything manually.
```

### After (with faker integration):
```
Visit: http://localhost:8000/client/create/

Form fields are pre-populated:
┌─────────────────────────────────────┐
│ Name:         [Acme Corporation   ]  │
│ Description:  [Innovative solutions] │
│ URL:          [https://example.com]  │
│                                     │
│         [Submit]  [Cancel]          │
└─────────────────────────────────────┘

User can just click Submit or modify as needed.
```

## Example 2: Creating a Contact (DEBUG=True)

```python
# View code
class ContactCreateView(FakeDataMixin, BaseContactView, CreateView):
    fake_data_function = 'get_fake_contact_data'
```

```
Generated fake data:
{
    'first_name': 'John',
    'last_name': 'Smith',
    'email': 'john.smith@example.com',
    'number': '+1-555-0123',
    'url': 'https://linkedin.com/in/johnsmith'
}
```

## Example 3: Production Behavior (DEBUG=False)

```python
# settings/production.py
DEBUG = False

# Result:
# - get_faker() returns None
# - All get_fake_*_data() functions return {}
# - Forms render with empty fields (normal behavior)
# - Zero performance impact
```

## Example 4: Preserving Existing Initial Values

```python
class ProjectCreateView(FakeDataMixin, BaseProjectView, CreateView):
    fake_data_function = 'get_fake_project_data'
    
    def get_initial(self):
        # Parent adds fake data
        initial = super().get_initial()
        
        # Then we add specific values
        client_id = self.request.GET.get("client_id")
        if client_id:
            client = Client.objects.get(id=client_id)
            initial["client"] = client  # This OVERRIDES fake data
        
        # Fake data is added for:
        # - name: "Revolutionary Platform"
        # - description: "Lorem ipsum dolor sit amet..."
        
        # But client is set from URL parameter
        
        return initial
```

Result:
```
initial = {
    'name': 'Revolutionary Platform',  # From faker
    'description': 'Lorem ipsum...',    # From faker
    'client': <Client: Microsoft>       # From URL parameter (overrides)
}
```

## Example 5: Custom Faker Function

If you want to add faker support to a new model:

```python
# 1. Add function to faker_utils.py
def get_fake_employee_data():
    """Generate fake data for Employee model."""
    fake = get_faker()
    if not fake:
        return {}
    
    return {
        'name': fake.name(),
        'title': fake.job(),
        'department': fake.random_element(['Engineering', 'Sales', 'HR']),
        'hire_date': fake.date_this_decade(),
    }

# 2. Update view to use the mixin
class EmployeeCreateView(FakeDataMixin, BaseEmployeeView, CreateView):
    fake_data_function = 'get_fake_employee_data'  # That's it!
```

## Example 6: Testing Faker Functions

```python
# From test_faker_utils.py
@override_settings(DEBUG=True)
def test_get_fake_client_data_returns_valid_data(self):
    """get_fake_client_data should return dict with expected keys."""
    result = get_fake_client_data()
    
    # Check structure
    self.assertIsInstance(result, dict)
    self.assertIn('name', result)
    self.assertIn('description', result)
    self.assertIn('url', result)
    
    # Check values are not empty
    self.assertTrue(result['name'])
    self.assertTrue(result['description'])
    self.assertTrue(result['url'])
```

## Example 7: Debugging

If fake data isn't appearing:

```python
# Check 1: Is DEBUG enabled?
from django.conf import settings
print(settings.DEBUG)  # Should be True

# Check 2: Is Faker installed?
try:
    from faker import Faker
    print("Faker is installed")
except ImportError:
    print("Faker is NOT installed - run: pip install Faker")

# Check 3: Is the mixin applied correctly?
from db.views.client import ClientCreateView
print(hasattr(ClientCreateView, 'fake_data_function'))  # Should be True
print(ClientCreateView.fake_data_function)  # Should be 'get_fake_client_data'

# Check 4: Does the function exist?
from db import faker_utils
func = getattr(faker_utils, 'get_fake_client_data', None)
print(f"Function exists: {func is not None}")
print(f"Function result: {func()}")
```

## Example 8: Performance Impact

```
Development (DEBUG=True):
- First request: ~50ms overhead (Faker import)
- Subsequent requests: ~5ms per form (data generation)
- Impact: Negligible for development

Production (DEBUG=False):
- Overhead: 0ms
- The code path is never executed
- if settings.DEBUG check happens first
```
