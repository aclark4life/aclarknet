Time Entry Relationships
=========================

This page describes how a ``Time`` entry's ``project``, ``task``, and
``invoice`` fields are populated, how that differs between admin
(superuser) and non-admin users, and how new time is automatically
matched to an existing invoice.

Model relationships
--------------------

- ``Time.project`` -> ``Project`` (optional foreign key)
- ``Time.task`` -> ``Task`` (optional foreign key)
- ``Time.invoice`` -> ``Invoice`` (optional foreign key)
- ``Project.default_task`` -> ``Task`` (optional foreign key, used as a
  fallback when a time entry has no task)
- ``Invoice.project`` -> ``Project``, plus ``Invoice.start_date`` /
  ``Invoice.end_date`` define the billing period an invoice covers

How the ``project`` field is populated
---------------------------------------

Unlike ``task``, there is **no automatic default** for ``project`` at
the model level. ``Time.save()`` (see ``db/models.py``) only defaults
``task``, never ``project``.

``project`` is a normal, required ``ModelChoiceField`` on ``TimeForm``
(``db/forms.py``), backed by the unfiltered ``Project.objects.all()``
queryset (ordered by ``Project.Meta.ordering = ["name"]``). This field
is **never removed or hidden** for non-admin users, so:

- Both admins and non-admins see the same visible ``project`` dropdown
  listing every project in the system.
- There is no per-user scoping of which projects appear (``Project``
  has no owner/user field), and no default is pre-selected.
- The user must manually choose a project every time they create a
  time entry, unless a query-string pre-fill applies (see below).

Query-string pre-fill (``?invoice_id=``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``TimeCreateView.get_context_data()`` (``db/views/time.py``) will
pre-populate the form's *initial* ``project`` value when the create
URL includes ``?invoice_id=<id>`` and that invoice has a project set.
This only sets the initial selection; the field remains editable and
this pre-fill only applies if the ``project`` field is present on the
form (it always is).

Admin-only dropdown cascade (JavaScript)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``frontend/src/utils/timeForm.js`` wires up a live cascade between the
``invoice``, ``project``, and ``task`` dropdowns using the
``time_api_invoice`` / ``time_api_project`` / ``time_api_task`` JSON
endpoints (``db/urls.py``):

- Changing **invoice** -> sets ``project`` to the invoice's project and
  ``task`` to that project's default task.
- Changing **project** -> sets ``task`` to that project's default task.
- Changing **task** -> sets ``project`` to that task's project.

This cascade only runs **when all three dropdowns
(``id_invoice``, ``id_project``, ``id_task``) are present on the page**.
Since ``invoice`` and ``task`` are removed from the form for non-admin
users (see below), the cascade is effectively admin-only; non-admins
just get the plain, unfiltered ``project`` select with no
auto-population.

Admin vs. non-admin form differences
--------------------------------------

``TimeForm.__init__`` (``db/forms.py``) adjusts fields based on the
user passed in from the view:

- **Admin (superuser)**: ``user`` field is shown as a visible
  ``Select`` (instead of hidden); ``invoice``, ``task``, and ``name``
  fields are shown.
- **Non-admin**: ``user`` stays hidden (defaults to the logged-in
  user); ``invoice``, ``task``, and ``name`` fields are removed
  entirely from the form.
- **``project``**: present and visible for *both* admins and
  non-admins; never hidden or removed.

Because non-admins never see ``task`` or ``invoice`` fields, those are
filled in automatically:

- ``task`` falls back to ``project.default_task``, or the global
  default from ``Task.get_default_task()`` (name
  "Software Development"), via ``Time.save()``.
- ``invoice`` is filled in by the auto-assignment signal described
  below.

Auto-assigning new time entries to an invoice
------------------------------------------------

Time entries are typically logged *after* an invoice period has
already been opened (rather than an invoice being created after time
already exists). To support that, a ``pre_save`` signal on ``Time``
(``db/signals.py::auto_assign_time_to_invoice``) automatically attaches
a **newly created**, unbilled entry to an existing invoice when:

- the entry has no ``invoice`` set yet (manual assignment is always
  respected and never overridden),
- it has a ``project`` set, and
- it has a ``date`` that falls within an ``Invoice.start_date`` /
  ``Invoice.end_date`` range for an invoice on that same project.

If more than one invoice matches (e.g. overlapping periods), the
invoice with the most recent ``start_date`` is preferred. Saves to an
*existing* time entry (i.e. one that already has a primary key) never
trigger auto-assignment, only creation does.

See ``db/tests/test_signals.py::TimeAutoAssignInvoiceSignalTest`` for
the covered scenarios.
