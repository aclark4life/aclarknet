Notes Import Documentation
==========================

This document describes the tools created to import notes from CSV files into the Django database.

Files Created
-------------

1. ``db/management/commands/import_notes.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Django management command to import notes from CSV files into the Note model.

**Features:**

- Imports notes with preserved timestamps (created/updated)
- Links notes to users via user_id field
- Handles missing users gracefully with ``--skip-missing-users`` flag
- Supports dry-run mode to preview imports
- Cleans up literal ``\r\n`` escape sequences in text
- Provides detailed progress reporting

**Usage:**

.. code-block:: bash

   # Basic import from notes_import.csv
   python manage.py import_notes

   # Import from cleaned CSV file
   python manage.py import_notes --file notes_import_cleaned.csv

   # Dry run to preview without creating notes
   python manage.py import_notes --file notes_import_cleaned.csv --dry-run

   # Skip notes with missing users instead of failing
   python manage.py import_notes --skip-missing-users

   # Import from a different file
   python manage.py import_notes --file /path/to/other_notes.csv

2. ``scripts/clean_notes_csv.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python script to clean up CSV files by converting HTML to plain text.

**Features:**

- Converts HTML content to readable plain text
- Removes HTML tags, entities, and formatting
- Converts lists to bullet points (•)
- Extracts URLs from links
- Normalizes whitespace and line endings
- Preserves CSV structure

**Usage:**

.. code-block:: bash

   # Clean the default file (notes_import.csv -> notes_import_cleaned.csv)
   python scripts/clean_notes_csv.py

   # Clean a custom file
   python scripts/clean_notes_csv.py input.csv output.csv

CSV File Format
---------------

The CSV file should have the following columns:

- ``id``: Original note ID (not used, Django creates new IDs)
- ``created``: Creation timestamp (format: ``YYYY-MM-DD HH:MM:SS.ffffff+TZ``)
- ``updated``: Last update timestamp (same format)
- ``name``: Note name/title
- ``description``: Note content/description
- ``user_id``: User ID to associate with note (optional)

Import Process
--------------

Step 1: Clean the CSV File
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python scripts/clean_notes_csv.py

This will:

- Read ``notes_import.csv``
- Convert HTML to plain text
- Clean up formatting
- Output to ``notes_import_cleaned.csv``

**Results:**

- Total rows processed: 77
- Rows with HTML cleaned: 68

Step 2: Preview the Import (Dry Run)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py import_notes --file notes_import_cleaned.csv --dry-run --skip-missing-users

This will show you what would be imported without actually creating any notes.

Step 3: Perform the Import
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python manage.py import_notes --file notes_import_cleaned.csv --skip-missing-users

This will create all the notes in the database.

Example Output
--------------

Cleaning Script Output
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Reading from: notes_import.csv
   Writing to: notes_import_cleaned.csv
   Row 3: Cleaned HTML from 'ACLARK.NET, LLC Meeting Notes- June 30 2020 10:00AM'
   Row 4: Cleaned HTML from 'ACLARK.NET, LLC Meeting Notes- Jul 7 2020 10:00AM'
   ...
   Processing complete!
   Total rows: 77
   Rows with HTML cleaned: 68
   Output saved to: notes_import_cleaned.csv

Import Script Output
~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Reading notes from: notes_import_cleaned.csv
   Row 2: Created note 'CostCo'
   Row 3: Created note 'Kensington CVS'
   ...
   ==================================================
   IMPORT COMPLETE
   Created: 77 notes

Notes
-----

- The ``--skip-missing-users`` flag is recommended if some notes don't have valid user IDs
- Original timestamps from the CSV are preserved in the database
- The cleaning script converts HTML entities and tags to readable text
- List items are converted to bullet points (•)
- Links are converted to "text (URL)" format
- Excessive whitespace is normalized

Troubleshooting
---------------

**Error: CSV file not found**

- Make sure you're running the command from the project root directory
- Check that the file path is correct

**Error: User with ID X not found**

- Use the ``--skip-missing-users`` flag to skip notes with invalid user IDs
- Or create the missing users first

**HTML still appears in notes**

- Make sure you ran the cleaning script first
- Use the cleaned CSV file (``notes_import_cleaned.csv``) for import
