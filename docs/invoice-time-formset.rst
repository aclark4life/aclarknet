Invoice Time Entry Formset Feature
==================================

Overview
--------

This feature adds the ability to add, edit, and remove time entries
directly from the invoice edit page using Django’s inline formset
functionality.

Changes Made
------------

1. Forms (db/forms.py)
~~~~~~~~~~~~~~~~~~~~~~

- **TimeEntryForm**: A simplified form for time entries in the formset
  with Bootstrap styling
- **TimeEntryFormSet**: An inline formset factory that connects Time
  entries to Invoices

The formset: - Displays 3 empty forms by default for adding new time
entries - Allows deletion of existing time entries via checkbox -
Includes fields: date, hours, description, project, task, user

2. Views (db/views/invoice.py)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updated **InvoiceUpdateView**: - Added custom template
``invoice_edit.html`` specifically for invoice editing - Integrated
formset in ``get_context_data()`` to handle both GET and POST requests -
Enhanced ``form_valid()`` to validate and save both the invoice form and
time entry formset

3. Template (db/templates/invoice_edit.html)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Created a dedicated template that: - Extends the dashboard layout -
Displays the main invoice form - Shows the time entry formset with
management form - Each time entry row includes: - Date picker - Hours
input - Project, Task, and User dropdowns - Description textarea -
Delete checkbox for existing entries - Responsive layout using Bootstrap
grid system

Usage
-----

Adding Time Entries
~~~~~~~~~~~~~~~~~~~

1. Navigate to an invoice’s edit page
2. Scroll to the “Time Entries” section
3. Fill in the empty forms at the bottom:

   - Select a date
   - Enter hours worked
   - Optionally select project, task, and user
   - Add a description if needed

4. Click “Save” to save all changes

Editing Time Entries
~~~~~~~~~~~~~~~~~~~~

1. Existing time entries appear at the top of the formset
2. Modify any field as needed
3. Click “Save” to update

Deleting Time Entries
~~~~~~~~~~~~~~~~~~~~~

1. Check the “Delete” checkbox next to the time entry you want to remove
2. Click “Save” to apply the deletion

Technical Details
-----------------

Formset Management
~~~~~~~~~~~~~~~~~~

Django’s formset includes a management form that tracks: - Total number
of forms (TOTAL_FORMS) - Number of initial forms (INITIAL_FORMS) -
Min/max number of forms

These are automatically handled by Django and included via
``{{ time_formset.management_form }}``.

Related Models
~~~~~~~~~~~~~~

- **Invoice**: The parent model
- **Time**: The child model with a ForeignKey to Invoice
- Relationship: ``invoice.times`` (related_name on Time model)

Validation
~~~~~~~~~~

The view validates both: 1. The main invoice form 2. The time entry
formset

Only if both are valid will the data be saved. If either fails
validation, the user is returned to the form with error messages.

Future Enhancements
-------------------

Potential improvements: - Dynamic add/remove buttons using JavaScript -
Real-time calculation of total hours and amounts - Auto-population of
task rates based on selected project - Inline editing without page
reload (AJAX) - Drag-and-drop reordering of time entries
