Fix Gmail Warning
=================

This guide shows you how to fix the "Be careful with this message" warning that Gmail displays for emails sent from your AWS SES setup.

Current Status
--------------

Based on DNS checks performed on 2026-02-01:

- SPF Record: Properly configured

  .. code-block:: text

     v=spf1 include:amazonses.com include:_spf.google.com ~all

- DMARC Record: **MISSING** - This is likely the main cause of the Gmail warning
- DKIM Records: Need to verify in AWS SES Console

Required Actions
----------------

1. Add DMARC Record (CRITICAL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add this TXT record to your DNS:

:Record Type: TXT
:Name/Host: ``_dmarc.aclark.net`` (or just ``_dmarc`` depending on your DNS provider)
:Value: ``v=DMARC1; p=quarantine; rua=mailto:aclark@aclark.net; pct=100``
:TTL: 3600 (or default)

**Explanation of DMARC policy:**

- ``p=quarantine``: Failed emails go to spam (use ``p=reject`` for stricter policy)
- ``rua=mailto:aclark@aclark.net``: Send aggregate reports to this email
- ``pct=100``: Apply policy to 100% of emails

**Alternative (less strict) DMARC policy for testing:**

.. code-block:: text

   v=DMARC1; p=none; rua=mailto:aclark@aclark.net; pct=100

2. Verify DKIM in AWS SES
~~~~~~~~~~~~~~~~~~~~~~~~~~

Step 1: Check if domain is verified in AWS SES
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Go to `AWS SES Console <https://console.aws.amazon.com/ses/>`__
2. Navigate to **Configuration** → **Verified identities**
3. Look for ``aclark.net`` (the domain, not just the email address)

Step 2: If domain is NOT verified
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Click **Create identity**
2. Select **Domain**
3. Enter ``aclark.net``
4. Check **Easy DKIM** (recommended)
5. Click **Create identity**

AWS will provide 3 CNAME records like:

.. code-block:: text

   Name: <token1>._domainkey.aclark.net
   Value: <token1>.dkim.amazonses.com

   Name: <token2>._domainkey.aclark.net
   Value: <token2>.dkim.amazonses.com

   Name: <token3>._domainkey.aclark.net
   Value: <token3>.dkim.amazonses.com

Step 3: Add DKIM CNAME records to your DNS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add all 3 CNAME records provided by AWS to your DNS provider.

3. Verify DNS Changes
~~~~~~~~~~~~~~~~~~~~~~

After adding the records, verify them:

.. code-block:: bash

   # Check DMARC
   dig TXT _dmarc.aclark.net +short

   # Check DKIM (replace <token> with actual tokens from AWS)
   dig CNAME <token1>._domainkey.aclark.net +short
   dig CNAME <token2>._domainkey.aclark.net +short
   dig CNAME <token3>._domainkey.aclark.net +short

   # Check SPF (should already be working)
   dig TXT aclark.net +short | grep spf

4. Test Email Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After DNS changes propagate (can take up to 48 hours, usually much faster):

1. Send a test email to your Gmail account
2. Open the email in Gmail
3. Click the three dots (⋮) → **Show original**
4. Look for these authentication results:

.. code-block:: text

   SPF: PASS
   DKIM: PASS
   DMARC: PASS

5. Code Improvements (Already Applied)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following improvements have been made to your email sending code:

- Created ``aclarknet/email_utils.py`` with improved email headers
- Updated ``db/signals.py`` to use new email utility
- Updated ``cms/views.py`` to use new email utility with proper Reply-To header

These changes add headers that improve deliverability:

- ``Reply-To``: Proper reply address
- ``X-Mailer``: Identifies sender application
- ``X-Auto-Response-Suppress``: Prevents auto-reply loops
- ``Precedence: bulk``: Indicates automated mail

Quick Reference
---------------

DNS Records Needed
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 10 30 40 20

   * - Type
     - Name
     - Value
     - Priority
   * - TXT
     - ``_dmarc.aclark.net``
     - ``v=DMARC1; p=quarantine; rua=mailto:aclark@aclark.net``
     - **CRITICAL**
   * - CNAME
     - ``<token1>._domainkey.aclark.net``
     - From AWS SES Console
     - High
   * - CNAME
     - ``<token2>._domainkey.aclark.net``
     - From AWS SES Console
     - High
   * - CNAME
     - ``<token3>._domainkey.aclark.net``
     - From AWS SES Console
     - High
   * - TXT
     - ``aclark.net``
     - ``v=spf1 include:amazonses.com include:_spf.google.com ~all``
     - Already set

Timeline
~~~~~~~~

- **Immediate**: Add DMARC record (5 minutes)
- **Within 1 hour**: Verify domain in AWS SES and add DKIM records
- **1-48 hours**: DNS propagation
- **After propagation**: Test and verify authentication passes

Troubleshooting
---------------

Gmail still shows warning after DNS changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Wait 24-48 hours for DNS propagation
- Clear Gmail cache (use incognito mode)
- Check authentication headers in "Show original"

DKIM not passing
~~~~~~~~~~~~~~~~

- Verify all 3 CNAME records are added correctly
- Check AWS SES Console shows domain as "Verified"
- Ensure DKIM signing is enabled in SES

DMARC not passing
~~~~~~~~~~~~~~~~~

- Verify DMARC record is added correctly
- Ensure FROM address matches verified domain (``aclark@aclark.net``)
- Check SPF and DKIM are both passing first

Additional Resources
--------------------

- `AWS SES DKIM Documentation <https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication-dkim.html>`__
- `DMARC.org <https://dmarc.org/>`__
- `MXToolbox DMARC Check <https://mxtoolbox.com/dmarc.aspx>`__
