aclarknet Documentation
=======================

Welcome to the aclarknet documentation! This is a Django-based web application using Wagtail CMS with a modern frontend stack.

This documentation follows the `Diátaxis <https://diataxis.fr/>`_ framework, organizing content into four types:

* **Tutorials** - Learning-oriented lessons for beginners
* **How-to Guides** - Goal-oriented directions for specific tasks
* **Reference** - Information-oriented technical descriptions
* **Explanation** - Understanding-oriented context and background

.. toctree::
   :maxdepth: 2
   :caption: Tutorials:

   tutorials/index

.. toctree::
   :maxdepth: 2
   :caption: How-to Guides:

   how-to/index

.. toctree::
   :maxdepth: 2
   :caption: Reference:

   reference/index

.. toctree::
   :maxdepth: 2
   :caption: Explanation:

   explanation/index

.. toctree::
   :maxdepth: 1
   :caption: Quick References:

   email-fix-summary

Getting Started
===============

**New to aclarknet?** Start with :doc:`tutorials/getting-started` to set up your development environment and create your first client.

**Need to accomplish a specific task?** Check out the :doc:`how-to/index` for goal-oriented guides.

**Looking for technical details?** See the :doc:`reference/index` for complete API documentation.

**Want to understand how it works?** Read the :doc:`explanation/index` for context and background.

Project Overview
================

This is a Django-based web application using Wagtail CMS with a modern frontend stack. The project combines Django's robust backend capabilities with Wagtail's powerful content management features, along with a React-based frontend built with Webpack.

Tech Stack
----------

Backend
~~~~~~~

* **Django 6.0**: Main web framework
* **Wagtail**: CMS framework for content management
* **MongoDB**: Database backend using ``django-mongodb-backend``
* **Django Allauth**: Authentication and social account management
* **Django reCAPTCHA**: Google reCAPTCHA v3 integration for form protection
* **Django SES**: AWS Simple Email Service integration
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

Key Features
------------

* **Client Management**: Categorize and feature clients on the public website
* **Notes & Testimonials**: Manage contact form submissions and client testimonials
* **Contact Form**: reCAPTCHA-protected contact form with email notifications
* **Email Integration**: AWS SES integration with IAM role support
* **Wagtail CMS**: Powerful content management system
* **Modern Frontend**: React-based UI with Tailwind CSS

Quick Links
-----------

* :doc:`tutorials/getting-started` - Get started with aclarknet
* :doc:`how-to/deployment-quickstart` - Deploy to production
* :doc:`how-to/testimonials-quickstart` - Manage testimonials
* :doc:`how-to/aws-ses-setup` - Configure email sending
* :doc:`how-to/fix-gmail-warning` - Fix Gmail email warnings
* :doc:`reference/db-views` - Database model reference
* :doc:`explanation/client-categorization` - Understand client categorization

Important
---------

**Gmail showing warnings for your emails?** See :doc:`email-fix-summary` for a quick fix, or :doc:`how-to/fix-gmail-warning` for detailed instructions.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
