aclarknet Documentation
=======================

Welcome to the aclarknet documentation! This is a Django-based web application using Wagtail CMS with a modern frontend stack.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Deployment
----------

.. toctree::
   :maxdepth: 2
   :caption: Deployment:

   deployment_guide
   deployment_quickstart
   SOCKET_ACTIVATION

Database
--------

.. toctree::
   :maxdepth: 2
   :caption: Database:

   db_views
   invoice_time_formset

Features
--------

.. toctree::
   :maxdepth: 2
   :caption: Features:

   notes_testimonials
   testimonials_quickstart

Frontend
--------

.. toctree::
   :maxdepth: 2
   :caption: Frontend:

   frontend
   frontend_application
   frontend_components

Project Overview
----------------

This is a Django-based web application using Wagtail CMS with a modern frontend stack. The project combines Django's robust backend capabilities with Wagtail's powerful content management features, along with a React-based frontend built with Webpack.

Tech Stack
----------

Backend
~~~~~~~

* **Django 6.0**: Main web framework
* **Wagtail**: CMS framework for content management
* **MongoDB**: Database backend using ``django-mongodb-backend``
* **Django Allauth**: Authentication and social account management
* **Python 3.13**: Target Python version

Frontend
~~~~~~~~

* **React 19**: UI library
* **Webpack 5**: Module bundler
* **Tailwind CSS 4**: Utility-first CSS framework
* **Bootstrap 5**: CSS framework
* **Babel**: JavaScript transpiler
* **SASS**: CSS preprocessor

Development Tools
~~~~~~~~~~~~~~~~~

* **Ruff**: Python linter and formatter
* **ESLint**: JavaScript linter
* **Stylelint**: CSS linter
* **pytest**: Testing framework
* **pre-commit**: Git hooks for code quality
* **just**: Command runner

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
