# Faker Integration Architecture

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Visits Create Form                     │
│                    (e.g., /client/create/)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 ClientCreateView.get_initial()                   │
│                 (inherits from FakeDataMixin)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Check DEBUG?   │
                    └───┬────────┬───┘
                        │        │
                  Yes   │        │   No
                        │        │
                        ▼        ▼
          ┌──────────────────┐  │
          │  Check Faker     │  │
          │  Available?      │  │
          └────┬─────────┬───┘  │
               │         │      │
          Yes  │         │ No   │
               │         │      │
               ▼         ▼      ▼
    ┌──────────────┐    └──────┴──────────┐
    │ Call         │                       │
    │ get_fake_    │    Return empty dict  │
    │ client_data()│    or parent initial  │
    └──────┬───────┘                       │
           │                               │
           ▼                               │
    ┌──────────────────────┐              │
    │ Faker generates      │              │
    │ fake data:           │              │
    │ - name               │              │
    │ - description        │              │
    │ - url                │              │
    └──────┬───────────────┘              │
           │                               │
           ▼                               │
    ┌──────────────────────┐              │
    │ Merge with existing  │              │
    │ initial values       │              │
    │ (don't override)     │              │
    └──────┬───────────────┘              │
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
             ┌─────────────────────────────┐
             │   Return initial dict        │
             │   to form                    │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌─────────────────────────────┐
             │   Form renders with          │
             │   pre-populated fields       │
             └─────────────────────────────┘
```

## Component Interactions

```
┌──────────────────┐
│  CreateView      │  Subclasses from FakeDataMixin
│  (e.g., Client)  │  Sets: fake_data_function = 'get_fake_client_data'
└────────┬─────────┘
         │
         │ inherits get_initial()
         │
         ▼
┌──────────────────┐
│  FakeDataMixin   │  Provides get_initial() method
└────────┬─────────┘  Checks DEBUG and calls faker_utils
         │
         │ imports and calls
         │
         ▼
┌──────────────────┐
│  faker_utils.py  │  Contains all fake data generation functions
└──────────────────┘  - get_fake_client_data()
                       - get_fake_company_data()
                       - get_fake_contact_data()
                       - etc.
```

## Key Design Principles

1. **DRY (Don't Repeat Yourself)**
   - All fake data generation in one place (faker_utils.py)
   - Reusable mixin for all CreateViews

2. **Minimal Changes**
   - Only modified view files to add mixin and one line config
   - No changes to forms, models, or templates

3. **Safe**
   - Only activates in DEBUG mode
   - Gracefully handles missing Faker library
   - Never overwrites existing initial values

4. **Testable**
   - Comprehensive unit tests
   - Standalone verification script
   - Clear separation of concerns
