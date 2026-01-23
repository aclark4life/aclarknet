# Notes as Testimonials Feature

## Overview
This feature enables the use of Notes to display testimonials on the public-facing site. Notes can now be marked as testimonials and will appear on the `/clients/` page and optionally as a featured testimonial on the homepage.

## Changes Made

### 1. Model Changes (`db/models.py`)
Added three new fields to the `Note` model:

- **`is_testimonial`** (BooleanField)
  - Default: `False`
  - Help text: "Check to display this note as a testimonial on the public site"
  
- **`title`** (CharField, max_length=300)
  - Optional field for the testimonial author's position/title
  - Example: "CEO", "Project Manager", "Head of Operations"
  - Help text: "Title/position of the person giving the testimonial"
  
- **`is_featured`** (BooleanField)
  - Default: `False`
  - Help text: "Check to feature this testimonial on the homepage"
  - Only one testimonial should typically be featured at a time

### 2. Database Migration (`db/migrations/0003_note_testimonial_fields.py`)
- Adds the three new fields to the Note model
- Compatible with the MongoDB backend used by the project

### 3. Admin Changes (`db/admin.py`)
Enhanced `NoteAdmin` with:
- Added `is_testimonial`, `is_featured`, and `title` to `list_display`
- Added `is_testimonial` and `is_featured` to `list_filter` for easy filtering
- Updated search fields to use `description` instead of deprecated `text` field

### 4. View Changes (`cms/views.py`)

#### ClientsView
- Queries for Notes with `is_testimonial=True`
- Orders testimonials by creation date (newest first)
- Passes `testimonials` list to the template context
- Falls back to empty list if database is unavailable

#### HomeView
- Queries for a single featured testimonial (`is_testimonial=True` and `is_featured=True`)
- Gets the most recently created featured testimonial
- Passes `testimonial` to the template context
- Falls back to `None` if no featured testimonial exists

### 5. Existing Templates (No Changes Required)
The following templates already expect testimonial data:

- **`cms/templates/blocks/testimonials_block.html`**
  - Displays all testimonials on the `/clients/` page
  - Uses `testimonial.description` for the quote
  - Uses `testimonial.name` for the author name
  - Uses `testimonial.title` for the author's position
  
- **`cms/templates/blocks/highpraise_block.html`**
  - Displays the featured testimonial on the homepage
  - Uses similar structure with description, name, and title
  - Includes fallback defaults if no testimonial is available

## How to Use

### 1. Apply the Migration
```bash
python manage.py migrate db
```

### 2. Create a Testimonial Note
In the Django admin at `/admin/db/note/`:
1. Click "Add Note"
2. Fill in the fields:
   - **Name**: The person's name (e.g., "John Smith")
   - **Description**: The testimonial quote (e.g., "They delivered exceptional results!")
   - **Title**: Their position (e.g., "CTO, Acme Corp")
   - **Is testimonial**: ✓ Check this box
   - **Is featured**: ✓ Check this to feature on homepage (optional)
3. Save the note

### 3. View Testimonials
- Visit `/clients/` to see all testimonials
- Visit `/` (homepage) to see the featured testimonial

## Example Usage

```python
from db.models import Note

# Create a regular testimonial
testimonial = Note.objects.create(
    name="Jane Doe",
    description="Working with this team was a game-changer for our organization!",
    title="VP of Engineering, Tech Corp",
    is_testimonial=True,
    is_featured=False
)

# Create a featured testimonial for the homepage
featured = Note.objects.create(
    name="John Smith",
    description="They exceeded all our expectations and delivered ahead of schedule.",
    title="CTO, Innovation Inc",
    is_testimonial=True,
    is_featured=True
)

# Query all testimonials
all_testimonials = Note.objects.filter(is_testimonial=True)

# Query featured testimonial
featured_testimonial = Note.objects.filter(
    is_testimonial=True, 
    is_featured=True
).order_by("-created").first()
```

## Admin Interface Tips

- Use the "Is testimonial" filter to quickly view all testimonials
- Use the "Is featured" filter to see which testimonial is currently featured
- Search by name or description text to find specific testimonials
- Only mark one testimonial as featured at a time for best results

## Template Variables

### In `testimonials_block.html` (Clients Page)
- `testimonials` - List of all Note objects with `is_testimonial=True`
- Each testimonial has:
  - `testimonial.description` - The quote text
  - `testimonial.name` or `testimonial` - The person's name
  - `testimonial.title` - Their position/title

### In `highpraise_block.html` (Homepage)
- `testimonial` - Single Note object with `is_testimonial=True` and `is_featured=True`
- Falls back to default text if None

## Notes

- Non-testimonial notes (`is_testimonial=False`) will NOT appear on public pages
- Multiple featured testimonials can exist, but only the most recent will be shown
- The feature is backward compatible - existing notes default to `is_testimonial=False`
- Notes can still be attached to other objects via the generic foreign key
- Testimonials don't require a `content_object` - they can be standalone
