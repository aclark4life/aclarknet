Getting Started with aclarknet
===============================

Set up aclarknet locally, then create a client entry and testimonial.

**Time required:** 30 minutes

**Prerequisites:**

* Python 3.13 installed
* MongoDB installed and running
* Basic familiarity with Django

.. note::

   Running the test suite (``pytest`` / ``just t``), as well as commands like
   ``makemigrations``/``migrate`` that need to inspect the database, requires
   a running MongoDB instance, since ``django-mongodb-backend`` connects to a
   real database. If no local ``mongod`` (or Docker) is available, start a
   throwaway instance with:

   .. code-block:: bash

      npx --yes mongodb-runner start --id aclarknet-test
      # prints a mongodb:// URI to use as MONGODB_URI, e.g.:
      export MONGODB_URI="mongodb://127.0.0.1:PORT/"

   Stop it afterward with ``npx mongodb-runner stop --id aclarknet-test``.

Step 1: Clone and Install
--------------------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/aclark4life/aclarknet.git
   cd aclarknet

   # Create a virtual environment
   python3.13 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -e '.[dev]'

Step 2: Configure Environment
------------------------------

Create a ``.env`` file for local development:

.. code-block:: bash

   # Copy the example environment file
   cp deployment/.env.example .env

Edit ``.env`` with your local settings:

.. code-block:: bash

   # Database
   MONGODB_URI=mongodb://localhost:27017/aclarknet

   # Django
   DEBUG=True
   SECRET_KEY=your-secret-key-here

   # reCAPTCHA (use test keys for development)
   RECAPTCHA_PUBLIC_KEY=6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI
   RECAPTCHA_PRIVATE_KEY=6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe

Step 3: Set Up the Database
----------------------------

Run migrations:

.. code-block:: bash

   python manage.py migrate --settings=aclarknet.settings.dev

Create a superuser:

.. code-block:: bash

   python manage.py createsuperuser --settings=aclarknet.settings.dev

Step 4: Run the Development Server
-----------------------------------

.. code-block:: bash

   python manage.py runserver --settings=aclarknet.settings.dev

Open http://localhost:8000

Step 5: Access the Admin Interface
-----------------------------------

Open http://localhost:8000/admin and sign in with your superuser account.

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

This client will appear on the public ``/clients/`` page because it is
featured.

Step 7: View Your Client
-------------------------

Open http://localhost:8000/clients/

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

Then open http://localhost:8000 to confirm the testimonial appears on
the homepage.

Next Steps
----------

* :doc:`deployment-quickstart` - Deploy to production
* :doc:`testimonials-quickstart` - Learn more about managing testimonials
* :doc:`db-views` - Explore the database models
* :doc:`client-categorization` - Understand client categorization
