DB Views Module
===============

This directory contains the refactored views for the ``db`` Django app.
The views have been organized into logical modules for better
maintainability and code organization.

Structure
---------

The views are organized as follows:

- **``base.py``** - Base classes, mixins, and error handlers

  - ``BaseView`` - Base view class with common functionality
  - ``SuperuserRequiredMixin`` - Require superuser access
  - ``AuthenticatedRequiredMixin`` - Require authenticated access
  - ``RedirectToObjectViewMixin`` - Redirect to object detail view
  - ``FilterByUserMixin`` - Filter objects by user
  - ``ModelCopyMixin`` - Generic copy behavior
  - Error handlers: ``custom_403``, ``custom_404``, ``custom_500``,
    ``trigger_500``

- **``client.py``** - Client model CRUD views

  - ``ClientListView``, ``ClientCreateView``, ``ClientDetailView``,
    ``ClientUpdateView``, ``ClientDeleteView``, ``ClientCopyView``

- **``company.py``** - Company model CRUD views

  - ``CompanyListView``, ``CompanyCreateView``, ``CompanyDetailView``,
    ``CompanyUpdateView``, ``CompanyDeleteView``, ``CompanyCopyView``

- **``contact.py``** - Contact model CRUD views

  - ``ContactListView``, ``ContactCreateView``, ``ContactDetailView``,
    ``ContactUpdateView``, ``ContactDeleteView``, ``ContactCopyView``

- **``dashboard.py``** - Dashboard and utility views

  - ``DashboardView`` - Main dashboard view
  - ``FakeTextView`` - Placeholder for fake text generation
  - Utility functions: ``display_mode``, ``html_mode``, ``lounge``,
    ``save_positions``

- **``invoice.py``** - Invoice model CRUD and export views

  - ``InvoiceListView``, ``InvoiceCreateView``, ``InvoiceDetailView``,
    ``InvoiceUpdateView``, ``InvoiceDeleteView``, ``InvoiceCopyView``
  - ``InvoiceExportPDFView`` - Export invoice as PDF
  - ``InvoiceEmailPDFView`` - Email invoice as PDF

- **``note.py``** - Note model CRUD and email views

  - ``NoteListView``, ``NoteListFullScreen``, ``NoteCreateView``,
    ``NoteDetailView``, ``NoteUpdateView``, ``NoteDeleteView``,
    ``NoteCopyView``
  - ``NoteEmailTextView`` - Email note as text

- **``project.py``** - Project model CRUD views

  - ``ProjectListView``, ``ProjectCreateView``, ``ProjectDetailView``,
    ``ProjectUpdateView``, ``ProjectDeleteView``, ``ProjectCopyView``

- **``search.py``** - Search functionality

  - ``SearchView`` - Search across multiple models

- **``task.py``** - Task model CRUD views

  - ``TaskListView``, ``TaskCreateView``, ``TaskDetailView``,
    ``TaskUpdateView``, ``TaskDeleteView``, ``TaskCopyView``

- **``time.py``** - Time entry CRUD views

  - ``TimeListView``, ``TimeCreateView``, ``TimeDetailView``,
    ``TimeUpdateView``, ``TimeDeleteView``, ``TimeCopyView``

- **``user.py``** - User management views

  - ``UserListView``, ``UserDetailView``, ``UserCreateView``,
    ``UserUpdateView``, ``UserDeleteView``, ``UserCopyView``

- **``utils.py``** - Utility functions

  - ``archive`` - Archive/unarchive objects
  - ``get_model_config`` - Get model configuration for bulk operations
  - ``update_selected_entries`` - Bulk update entries
  - ``update_related_entries`` - Update related entries

Usage
-----

All views are exported from the package ``__init__.py``, so you can
import them as before:

.. code:: python

   from db.views import ClientListView, InvoiceDetailView, DashboardView

Or import everything:

.. code:: python

   from db import views

Benefits of This Structure
--------------------------

1. **Better Organization** - Related views are grouped together in
   logical modules
2. **Easier Navigation** - Find specific views quickly by looking at the
   appropriate module
3. **Reduced Complexity** - Each file is smaller and more focused
4. **Improved Maintainability** - Changes to one model’s views don’t
   affect others
5. **Clear Responsibilities** - Each module has a clear purpose
6. **Backward Compatible** - All imports still work as before through
   ``__init__.py``

Migration Notes
---------------

This refactoring is **backward compatible**. All existing imports will
continue to work without changes to the rest of the codebase.

The previous monolithic ``views.py`` file (2271 lines) has been split
into 15 focused modules, making the codebase more maintainable while
preserving all functionality.
