Client Categorization Feature
=============================

Overview
--------

This feature adds the ability to designate specific clients to be
displayed on the public ``/clients/`` page and categorize them into
groups like Government, Non-profit, Private Sector, etc.

Changes Made
------------

1. Model Changes (``db/models.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added ``featured`` boolean field to the ``Client`` model

  - Default: ``False``
  - Help text: “Check to display this client on the public clients page”

- Added ``category`` field with predefined choices:

  - Government
  - Non-Profit
  - Private Sector
  - Education
  - Healthcare
  - Other

- The ``ClientCategory`` enum is defined as a nested class in the
  ``Client`` model

2. Database Migration (``db/migrations/0002_client_featured_category.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Creates migration to add both ``featured`` and ``category`` fields
- The migration is compatible with the MongoDB backend used by the
  project

3. Form Changes (``db/forms.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Updated ``ClientForm`` to include:

  - ``featured`` field
  - ``category`` field

- Added these fields to the form layout

4. Admin Changes (``db/admin.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Enhanced ``ClientAdmin`` with:

  - ``list_display`` showing name, company, category, and featured
    status
  - ``list_filter`` for filtering by featured status and category
  - ``search_fields`` for searching by client name or company name

5. View Changes (``cms/views.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Updated ``ClientsView`` to:

  - Filter only ``featured=True`` clients
  - Group clients by their category
  - Pass a ``categories`` dictionary to the template
  - Each category key maps to a list of clients in that category

6. Template Changes (``cms/templates/blocks/clients_block.html``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Fixed the URL check to use ``client.url`` instead of ``client.link``
- The template already supports displaying clients grouped by categories

7. Tests (``db/tests/test_client_categorization.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Added comprehensive test coverage:

  - Test featured field default value
  - Test category choices
  - Test category display names
  - Test filtering featured clients
  - Test grouping clients by category
  - Test the ClientsView context data

How to Use
----------

1. Apply the Migration
~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   python manage.py migrate db

2. Mark Clients as Featured
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the Django admin at ``/admin/db/client/``: 1. Edit a client record 2.
Check the “Featured” checkbox 3. Select a category from the dropdown 4.
Save the client

3. View Featured Clients
~~~~~~~~~~~~~~~~~~~~~~~~

Visit ``/clients/`` to see the featured clients grouped by category.

Example Usage
-------------

.. code:: python

   # Create a featured government client
   client = Client.objects.create(
       name="US Department of Example",
       featured=True,
       category=Client.ClientCategory.GOVERNMENT,
       url="https://example.gov"
   )

   # Query all featured clients
   featured_clients = Client.objects.filter(featured=True)

   # Query clients by category
   gov_clients = Client.objects.filter(
       featured=True,
       category=Client.ClientCategory.GOVERNMENT
   )

   # Get display name for category
   display_name = client.get_category_display()  # Returns "Government"

Testing
-------

Run the tests with:

.. code:: bash

   python manage.py test db.tests.test_client_categorization

Or with pytest:

.. code:: bash

   pytest db/tests/test_client_categorization.py

Notes
-----

- Non-featured clients (featured=False) will NOT appear on the public
  clients page
- Clients without a category will be grouped under “Other”
- The feature is backward compatible - existing clients default to
  featured=False
- The admin interface provides easy filtering and searching capabilities
