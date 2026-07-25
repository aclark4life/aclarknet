Manual Testing Guide for Client Categorization Feature
======================================================

Prerequisites
-------------

1. Install dependencies: ``pip install -e .`` or ``just i``
2. Run migrations: ``python manage.py migrate`` or ``just m``
3. Create a superuser if needed: ``python manage.py createsuperuser`` or
   ``just su``

Testing Steps
-------------

1. Create Featured Clients via Django Admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Start the development server:

   .. code:: bash

      python manage.py runserver
      # or
      just s

2. Navigate to the Django Admin: http://localhost:8000/admin/

3. Go to “Clients” section

4. Create or edit clients with the following attributes:

   **Government Client:**

   - Name: “US Department of Example”
   - Featured: ✓ (checked)
   - Category: “Government”
   - URL: https://example.gov (optional)

   **Non-Profit Client:**

   - Name: “Example Foundation”
   - Featured: ✓ (checked)
   - Category: “Non-Profit”
   - URL: https://example-foundation.org (optional)

   **Private Sector Client:**

   - Name: “ACME Corporation”
   - Featured: ✓ (checked)
   - Category: “Private Sector”
   - URL: https://acme.com (optional)

   **Hidden Client:**

   - Name: “Internal Client”
   - Featured: ☐ (unchecked)
   - Category: “Private Sector”

2. Verify in Django Admin
~~~~~~~~~~~~~~~~~~~~~~~~~

1. In the Clients list view, you should see:

   - Columns for Name, Company, Category, and Featured
   - Filter options on the right for Featured and Category
   - Search box that searches by client name or company name

2. Test the filters:

   - Click “Featured: Yes” to see only featured clients
   - Click “Featured: No” to see only non-featured clients
   - Click different categories to filter by category

3. Verify on Public Clients Page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to: http://localhost:8000/clients/

2. You should see:

   - Clients grouped by their categories (Government, Non-Profit,
     Private Sector, etc.)
   - Only clients marked as “Featured” are displayed
   - The “Internal Client” (not featured) should NOT appear
   - If a client has a URL, it should be clickable

3. Expected layout:

   ::

      A partial list of valued clients

      GOVERNMENT              NON-PROFIT           PRIVATE SECTOR
      - US Department        - Example            - ACME Corporation
        of Example            Foundation

4. Test Django Dashboard (Internal View)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to: http://localhost:8000/dashboard/client

2. You should see:

   - All clients (both featured and non-featured)
   - This is the internal management view
   - You can create, edit, and delete clients

5. Test Client Form
~~~~~~~~~~~~~~~~~~~

1. Click “Create Client” in the dashboard
2. Verify that the form includes:

   - Name field
   - URL field
   - Description field
   - Featured checkbox
   - Category dropdown with all available options

3. Create a new client with:

   - Featured: checked
   - Category: “Education”

4. Save and verify it appears on the public clients page under
   “Education”

Expected Results
----------------

| ✓ Featured clients appear on the public /clients/ page
| ✓ Non-featured clients do NOT appear on the public page
| ✓ Clients are grouped by their category
| ✓ Categories are displayed as headers (Government, Non-Profit, etc.)
| ✓ Client URLs are clickable when provided
| ✓ Admin list shows featured status and category
| ✓ Admin filters work correctly
| ✓ Form includes both new fields

Troubleshooting
---------------

**Issue: Changes not visible on the public page** - Solution: Make sure
the client is marked as “Featured” - Clear browser cache or hard refresh
(Ctrl+Shift+R or Cmd+Shift+R)

**Issue: Categories not showing** - Solution: Make sure at least one
featured client has a category assigned - Check that the category field
is not empty

**Issue: Migration errors** - Solution: Run
``python manage.py migrate db`` to apply the migration - If issues
persist, check MongoDB connection

**Issue: 500 error on clients page** - Solution: Check Django logs for
errors - Verify that the db.models.Client import works in cms/views.py -
Ensure all dependencies are installed

Clean Up After Testing
----------------------

To reset test data: 1. Navigate to Django Admin 2. Select all test
clients 3. Choose “Delete selected clients” from the actions dropdown 4.
Confirm deletion

Or use Django shell:

.. code:: python

   python manage.py shell
   >>> from db.models import Client
   >>> Client.objects.filter(name__icontains="test").delete()
