aclarknet Documentation
=======================

Documentation is organized as a flat set of topic-focused pages grouped
below by area.

.. toctree::
   :maxdepth: 1
   :caption: Getting Started:

   getting-started

.. toctree::
   :maxdepth: 1
   :caption: Deployment & Server Operations:

   deployment-quickstart
   deployment-guide
   ec2-iam-role-setup
   letsencrypt-renewal
   managing-dependencies

.. toctree::
   :maxdepth: 1
   :caption: Email:

   aws-ses-setup
   fix-gmail-warning
   email-authentication
   email-dns-records
   email-utilities
   email-fix-summary

.. toctree::
   :maxdepth: 1
   :caption: Clients & Testimonials:

   client-categorization
   feature-visual-guide
   testimonials-quickstart
   notes-testimonials
   notes-import

.. toctree::
   :maxdepth: 1
   :caption: Invoicing:

   invoice-dashboard-design
   invoice-time-formset
   copy-invoice-data
   time-entry-relationships

.. toctree::
   :maxdepth: 1
   :caption: Payments:

   stripe-test-mode

.. toctree::
   :maxdepth: 1
   :caption: Features:

   feedwell

.. toctree::
   :maxdepth: 1
   :caption: Testing:

   manual-testing-guide

.. toctree::
   :maxdepth: 1
   :caption: Reference:

   db-views
   frontend
   frontend-application
   frontend-components
   design-system

Getting Started
===============

- **New here?** Start with :doc:`getting-started`.
- **Need a task guide?** Use the sidebar sections such as *Deployment &
  Server Operations* or *Email*.
- **Need implementation detail?** See the *Reference* section.

Project Overview
================

aclarknet is a Django/Wagtail application with a React/Webpack frontend.

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
* **Wagtail CMS**: Content management system
* **feedwell**: Unified social media feed (Mastodon, Bluesky) at ``/feedwell/``
* **Modern Frontend**: React-based UI with Tailwind CSS

Quick Links
-----------

* :doc:`getting-started` - Get started with aclarknet
* :doc:`deployment-quickstart` - Deploy to production
* :doc:`letsencrypt-renewal` - Automate SSL certificate renewal
* :doc:`testimonials-quickstart` - Manage testimonials
* :doc:`aws-ses-setup` - Configure email sending
* :doc:`fix-gmail-warning` - Fix Gmail email warnings
* :doc:`db-views` - Database model reference
* :doc:`client-categorization` - Understand client categorization

Important
---------

**Gmail showing warnings for your emails?** See :doc:`email-fix-summary`
for the short version, or :doc:`fix-gmail-warning` for full instructions.

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
