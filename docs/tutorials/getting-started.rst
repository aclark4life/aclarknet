Getting Started with aclarknet
===============================

Welcome! This tutorial will guide you through setting up aclarknet for local development and creating your first client entry.

**What you'll learn:**

* How to set up the development environment
* How to run the application locally
* How to create your first client
* How to add a testimonial

**Time required:** 30 minutes

**Prerequisites:**

* Python 3.13 installed
* MongoDB installed and running
* Basic familiarity with Django

Step 1: Clone and Install
--------------------------

First, let's get the code and install dependencies:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/aclark4life/aclarknet.git
   cd aclarknet

   # Create a virtual environment
   python3.13 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -e '.[dev]'

**What just happened?** You've installed aclarknet and all its development dependencies, including Django, Wagtail, and the testing tools.

Step 2: Configure Environment
------------------------------

Create a ``.env`` file for local development:

.. code-block:: bash

   # Copy the example environment file
   cp deployment/.env.example .env

Edit the ``.env`` file with your settings:

.. code-block:: bash

   # Database
   MONGODB_URI=mongodb://localhost:27017/aclarknet

   # Django
   DEBUG=True
   SECRET_KEY=your-secret-key-here

   # reCAPTCHA (use test keys for development)
   RECAPTCHA_PUBLIC_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
   RECAPTCHA_PRIVATE_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe

**What just happened?** You've configured the application to use your local MongoDB and set up test reCAPTCHA keys that always pass validation.

Step 3: Set Up the Database
----------------------------

Run migrations to create the database structure:

.. code-block:: bash

   python manage.py migrate --settings=aclarknet.settings.dev

Create a superuser account:

.. code-block:: bash

   python manage.py createsuperuser --settings=aclarknet.settings.dev

**What just happened?** Django created all the necessary database collections in MongoDB and you created an admin account.

Step 4: Run the Development Server
-----------------------------------

Start the server:

.. code-block:: bash

   python manage.py runserver --settings=aclarknet.settings.dev

Open your browser to http://localhost:8000

**What you should see:** The aclarknet homepage with navigation and content.

Step 5: Access the Admin Interface
-----------------------------------

Navigate to http://localhost:8000/admin and log in with your superuser credentials.

**What you should see:** The Django admin interface with sections for Clients, Notes, Invoices, and more.

Step 6: Create Your First Client
---------------------------------

In the admin interface:

1. Click **"Clients"** in the left sidebar
2. Click **"Add Client"** button
3. Fill in the form:

   * **Name:** Example Corporation
   * **Featured:** Check this box
   * **Category:** Select "Private Sector"
   * **URL:** https://example.com

4. Click **"Save"**

**What just happened?** You created a client entry that will appear on the public ``/clients/`` page because you marked it as "featured".

Step 7: View Your Client
-------------------------

Navigate to http://localhost:8000/clients/

**What you should see:** Your "Example Corporation" client listed under the "Private Sector" category.

Step 8: Add a Testimonial
--------------------------

Back in the admin interface:

1. Click **"Notes"** in the left sidebar
2. Click **"Add Note"** button
3. Fill in the form:

   * **Name:** John Doe
   * **Email:** john@example.com
   * **How did you hear about us:** Select an option
   * **How can we help:** This is a testimonial
   * **Is testimonial:** Check this box
   * **Featured:** Check this box

4. Click **"Save"**

Navigate to http://localhost:8000

**What you should see:** Your testimonial displayed on the homepage.

Next Steps
----------

Congratulations! You've successfully set up aclarknet and created your first client and testimonial.

**Where to go from here:**

* :doc:`../how-to/deployment-quickstart` - Deploy to production
* :doc:`../how-to/testimonials-quickstart` - Learn more about managing testimonials
* :doc:`../reference/db-views` - Explore the database models
* :doc:`../explanation/client-categorization` - Understand how client categorization works
