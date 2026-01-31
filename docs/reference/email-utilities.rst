Email Utilities Reference
==========================

This document describes the email utility functions available in ``aclarknet/email_utils.py``.

Module: aclarknet.email_utils
------------------------------

This module provides improved email sending functions with proper headers for better deliverability and authentication.

Functions
---------

send_email_with_headers
~~~~~~~~~~~~~~~~~~~~~~~

Send email with proper headers for better deliverability and authentication.

**Signature:**

.. code-block:: python

   def send_email_with_headers(
       subject,
       plain_message,
       recipient_list,
       html_message=None,
       from_email=None,
       reply_to=None,
       fail_silently=False,
   )

**Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``subject``
     - str
     - Email subject line
   * - ``plain_message``
     - str
     - Plain text message body
   * - ``recipient_list``
     - list
     - List of recipient email addresses
   * - ``html_message``
     - str (optional)
     - HTML version of the message
   * - ``from_email``
     - str (optional)
     - Sender email (defaults to ``DEFAULT_FROM_EMAIL``)
   * - ``reply_to``
     - str (optional)
     - Reply-to address (defaults to ``from_email``)
   * - ``fail_silently``
     - bool (optional)
     - Whether to suppress exceptions (default: False)

**Returns:**

:Type: int
:Description: Number of successfully sent emails

**Headers Added:**

This function automatically adds the following headers to improve deliverability:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Header
     - Purpose
   * - ``Reply-To``
     - Specifies where replies should go
   * - ``X-Mailer: aclark.net``
     - Identifies the sending application
   * - ``X-Auto-Response-Suppress: OOF, AutoReply``
     - Prevents auto-reply loops
   * - ``Precedence: bulk``
     - Indicates automated mail

**Example Usage:**

.. code-block:: python

   from aclarknet.email_utils import send_email_with_headers

   send_email_with_headers(
       subject="Welcome to aclark.net",
       plain_message="Thank you for signing up!",
       recipient_list=["user@example.com"],
       html_message="<p>Thank you for signing up!</p>",
       from_email="aclark@aclark.net",
       reply_to="support@aclark.net",
   )

send_notification_email
~~~~~~~~~~~~~~~~~~~~~~~

Send a notification email to the site admin.

This is a convenience wrapper for internal notifications.

**Signature:**

.. code-block:: python

   def send_notification_email(
       subject,
       plain_message,
       html_message=None,
       from_email=None,
       recipient_email=None,
   )

**Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Parameter
     - Type
     - Description
   * - ``subject``
     - str
     - Email subject line
   * - ``plain_message``
     - str
     - Plain text message body
   * - ``html_message``
     - str (optional)
     - HTML version of the message
   * - ``from_email``
     - str (optional)
     - Sender email (defaults to ``DEFAULT_FROM_EMAIL``)
   * - ``recipient_email``
     - str (optional)
     - Recipient email (defaults to ``DEFAULT_FROM_EMAIL``)

**Returns:**

:Type: int
:Description: Number of successfully sent emails

**Example Usage:**

.. code-block:: python

   from aclarknet.email_utils import send_notification_email

   send_notification_email(
       subject="New contact form submission",
       plain_message="A user submitted the contact form.",
       html_message="<p>A user submitted the contact form.</p>",
   )

Usage in Application
--------------------

db/signals.py
~~~~~~~~~~~~~

The ``send_email_on_time_creation`` signal uses ``send_notification_email`` to send notifications when Time objects are created:

.. code-block:: python

   from aclarknet.email_utils import send_notification_email

   @receiver(post_save, sender=Time)
   def send_email_on_time_creation(sender, instance, created, **kwargs):
       if created:
           # ... prepare email content ...
           send_notification_email(
               subject=subject,
               plain_message=plain_message,
               html_message=html_content,
               from_email=from_email,
           )

cms/views.py
~~~~~~~~~~~~

The ``ContactView`` uses ``send_email_with_headers`` to send contact form notifications with proper Reply-To headers:

.. code-block:: python

   from aclarknet.email_utils import send_email_with_headers

   send_email_with_headers(
       subject=email_subject,
       plain_message=email_body,
       recipient_list=[contact_email],
       from_email=settings.DEFAULT_FROM_EMAIL,
       reply_to=email,  # Set to contact form submitter's email
       fail_silently=False,
   )

Benefits
--------

Using these utility functions provides several benefits:

1. **Consistent Headers**: All emails include proper headers for better deliverability
2. **Authentication Support**: Headers help with SPF, DKIM, and DMARC authentication
3. **Spam Prevention**: Proper headers reduce the chance of emails being marked as spam
4. **Reply Management**: Reply-To headers ensure replies go to the correct address
5. **Auto-Reply Prevention**: X-Auto-Response-Suppress prevents auto-reply loops
6. **Code Reuse**: Centralized email sending logic reduces code duplication

See Also
--------

- :doc:`../explanation/email-authentication` - Understanding email authentication
- :doc:`../how-to/fix-gmail-warning` - Fixing Gmail warnings
- :doc:`email-dns-records` - DNS records reference
