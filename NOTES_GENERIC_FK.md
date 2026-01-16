# Generic Foreign Key for Notes

This document describes how to use the generic foreign key functionality to attach notes to any model in the application.

## Overview

The `Note` model now supports generic foreign keys, allowing notes to be attached to any object in the database (Company, Client, Project, Invoice, Task, Time, Contact, etc.).

## Model Changes

The `Note` model now includes:
- `content_type`: ForeignKey to ContentType (identifies the model type)
- `object_id`: CharField (stores the object's primary key)
- `content_object`: GenericForeignKey (provides easy access to the related object)

## Creating Notes Attached to Objects

### Via Django Admin

1. Go to the Django admin interface
2. Navigate to Notes
3. Create a new note
4. Select the "Content type" from the dropdown (e.g., "db | company")
5. Enter the "Object id" (the primary key of the object you want to attach the note to)
6. Fill in the note name, text, and user fields
7. Save

### Via Python Code

```python
from django.contrib.contenttypes.models import ContentType
from db.models import Note, Company

# Get the company you want to attach a note to
company = Company.objects.get(name="Example Company")

# Get the content type for the Company model
content_type = ContentType.objects.get_for_model(Company)

# Create the note
note = Note.objects.create(
    name="Important Company Note",
    text="This company needs special attention for the upcoming project.",
    user=request.user,  # or any User instance
    content_type=content_type,
    object_id=str(company.pk)
)

# You can also access the related object via content_object
print(note.content_object)  # Returns the Company instance
```

## Retrieving Notes for an Object

```python
from django.contrib.contenttypes.models import ContentType
from db.models import Note, Company

# Get the company
company = Company.objects.get(name="Example Company")

# Get all notes for this company
content_type = ContentType.objects.get_for_model(Company)
notes = Note.objects.filter(
    content_type=content_type,
    object_id=str(company.pk)
).order_by('-created')

# Iterate over notes
for note in notes:
    print(f"{note.name}: {note.text}")
```

## Display in Detail Views

Notes are automatically displayed in detail views for all models. When viewing an object (Company, Client, Project, etc.) in the detail view, any notes attached to that object will appear in a dedicated "Notes" accordion section below the main details.

The notes section includes:
- Note name (if provided)
- Note text
- Author (user who created the note)
- Creation timestamp

## Standalone Notes

Notes can still be created without being attached to any object. Simply leave the `content_type` and `object_id` fields blank when creating the note.

```python
note = Note.objects.create(
    name="General Note",
    text="This is a general note not attached to any specific object",
    user=request.user
)
```

## Migration

The migration `db/migrations/0002_note_generic_foreign_key.py` adds the `content_type` and `object_id` fields to the Note model. Run migrations to apply these changes:

```bash
python manage.py migrate db
```

## Testing

Tests for the generic foreign key functionality are available in `db/tests/test_note_generic_fk.py`. Run them with:

```bash
python manage.py test db.tests.test_note_generic_fk
```

## Benefits

1. **Flexibility**: Attach notes to any model without modifying the model's schema
2. **Centralized**: All notes are stored in one table
3. **Easy Querying**: Retrieve all notes for any object using ContentType
4. **Automatic Display**: Notes automatically appear in detail views
5. **No Database Changes**: Can add notes to new models without migrations

## Limitations

1. **No Reverse Relation**: You cannot access notes from the related object using `object.notes.all()`. You must query through ContentType.
2. **Manual Object ID**: When creating notes via admin, you must manually enter the object ID.
3. **CharField for ID**: Object IDs are stored as CharField to support MongoDB ObjectIds and other non-integer IDs.

## Future Enhancements

Potential improvements that could be added:
1. Inline admin for notes in other model admin pages
2. API endpoints for creating/retrieving notes
3. Note notifications when notes are added
4. Note editing and deletion permissions
5. Note categories or tags
