Testimonials Quick Start Guide
================================

This guide shows you how to add and manage testimonials on your ACLARK.NET site.

Step 1: Access the Admin Interface
-----------------------------------

1. Navigate to ``/admin/`` on your site
2. Log in with your admin credentials
3. Click on "Notes" under the "DB" section

Step 2: Create a New Testimonial
---------------------------------

Click the "Add Note +" button and fill in the required fields.

Example Testimonial #1 (Featured)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   Name: Sarah Johnson
   Description: "ACLARK.NET transformed our development workflow. Their expertise in Python and Django is unmatched!"
   Title: CTO, TechVentures Inc
   Is testimonial: ✓ (checked)
   Is featured: ✓ (checked)

Example Testimonial #2 (Regular)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   Name: Michael Chen
   Description: "Professional, reliable, and always delivers quality work on time."
   Title: Director of Engineering, DataFlow Systems
   Is testimonial: ✓ (checked)
   Is featured: ☐ (unchecked)

Example Testimonial #3 (Regular)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   Name: Emily Rodriguez
   Description: "Their deep knowledge of Wagtail CMS helped us build an amazing content platform."
   Title: Product Manager, ContentHub
   Is testimonial: ✓ (checked)
   Is featured: ☐ (unchecked)

Step 3: View Your Testimonials
-------------------------------

On the Clients Page
~~~~~~~~~~~~~~~~~~~

1. Navigate to ``/clients/`` on your site
2. Scroll down to the "Client Feedback" section
3. You'll see all testimonials (Example #1, #2, and #3) displayed in a grid

On the Homepage
~~~~~~~~~~~~~~~

1. Navigate to ``/`` (homepage)
2. Look for the "Testimonials" section with a background image
3. You'll see only the featured testimonial (Example #1) displayed prominently

Managing Testimonials
---------------------

To Update a Testimonial
~~~~~~~~~~~~~~~~~~~~~~~

1. Go to ``/admin/db/note/``
2. Click on the testimonial you want to edit
3. Make your changes
4. Click "Save"

To Feature a Different Testimonial
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to ``/admin/db/note/``
2. Uncheck "Is featured" on the current featured testimonial
3. Check "Is featured" on the testimonial you want to feature
4. Save both notes

.. note::
   Only one testimonial should be featured at a time for best visual presentation.

To Filter/Search Testimonials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the admin, use the right sidebar filters:

- Filter by "Is testimonial"
- Filter by "Is featured"
- Filter by "Content type"

Use the search box to find testimonials by name or text.

Best Practices
--------------

1. **Keep quotes concise**: Aim for 1-2 sentences per testimonial
2. **Include full names**: Use real names with proper titles
3. **Be specific with titles**: Include company name if possible (e.g., "CTO, Acme Corp")
4. **Feature your best**: Choose your most compelling testimonial as featured
5. **Regular updates**: Rotate featured testimonials periodically to keep content fresh

Troubleshooting
---------------

Testimonials not showing on public pages?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Ensure "Is testimonial" checkbox is checked
- Verify the testimonial has both name and description fields filled

Featured testimonial not appearing on homepage?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Ensure "Is featured" checkbox is checked
- Verify "Is testimonial" is also checked
- Make sure the testimonial has all required fields (name, description, title)

Want to hide a testimonial temporarily?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Uncheck "Is testimonial" instead of deleting it
- This preserves the data while removing it from public view

Real-World Example
------------------

Here's what a complete testimonial entry looks like:

.. code-block:: text

   Name: Dr. Lisa Anderson
   Description: "Working with ACLARK.NET on our healthcare platform was exceptional. Their attention to security and compliance, combined with rapid development, made our project a huge success."
   Title: Chief Medical Information Officer, HealthTech Solutions
   User: (optional - link to user account if relevant)
   Content type: (optional - leave blank for standalone testimonials)
   Object id: (optional - leave blank for standalone testimonials)
   Is testimonial: ✓
   Is featured: ✓

Summary
-------

With the testimonials feature, you can:

- ✅ Display customer feedback on ``/clients/`` page
- ✅ Feature a standout testimonial on the homepage
- ✅ Easily manage testimonials through Django admin
- ✅ Filter and search testimonials
- ✅ Toggle visibility without deleting content

For more technical details, see :doc:`notes_testimonials`.
