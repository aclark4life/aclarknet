Gmail Warning Fix - Quick Summary
==================================

This document provides a quick summary of the Gmail warning fix. For detailed instructions, see the documentation links below.

Problem
-------

Gmail shows "Be careful with this message" warning for emails sent from your SES setup.

Root Cause
----------

**Missing DMARC record** - This is the primary issue causing the Gmail warning.

Current Status (as of 2026-02-01)
----------------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Authentication
     - Status
     - Details
   * - SPF
     - PASS
     - ``v=spf1 include:amazonses.com include:_spf.google.com ~all``
   * - DKIM
     - Unknown
     - Need to verify in AWS SES Console
   * - DMARC
     - **MISSING**
     - **This is causing the Gmail warning**

What Has Been Done
------------------

Code Improvements
~~~~~~~~~~~~~~~~~

- Created ``aclarknet/email_utils.py`` with improved email sending functions
- Updated ``db/signals.py`` to use new email utilities with better headers
- Updated ``cms/views.py`` to use new email utilities with proper Reply-To headers

New headers added to all emails:

- ``Reply-To``: Proper reply address
- ``X-Mailer: aclark.net``: Identifies your application
- ``X-Auto-Response-Suppress: OOF, AutoReply``: Prevents auto-reply loops
- ``Precedence: bulk``: Indicates automated mail

Diagnostic Tools
~~~~~~~~~~~~~~~~

- Created ``scripts/check_email_auth.sh`` - Check your current DNS authentication status
- Created ``scripts/test_email_headers.py`` - Send test emails to verify authentication

Documentation
~~~~~~~~~~~~~

- :doc:`how-to/fix-gmail-warning` - Step-by-step guide
- :doc:`reference/email-dns-records` - Complete DNS records reference
- :doc:`reference/email-utilities` - Email utilities API reference
- :doc:`explanation/email-authentication` - Understanding email authentication

What You Need to Do
-------------------

CRITICAL: Add DMARC Record (5 minutes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add this TXT record to your DNS provider:

:Name/Host: ``_dmarc.aclark.net`` (or just ``_dmarc``)
:Type: TXT
:Value: ``v=DMARC1; p=quarantine; rua=mailto:aclark@aclark.net; pct=100``
:TTL: 3600 (or default)

Important: Verify DKIM in AWS SES
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to https://console.aws.amazon.com/ses/
2. Navigate to **Configuration** → **Verified identities**
3. Check if ``aclark.net`` (the domain) is listed
4. If NOT listed:

   - Click **Create identity**
   - Select **Domain**
   - Enter ``aclark.net``
   - Enable **Easy DKIM**
   - AWS will provide 3 CNAME records

5. Add all 3 CNAME records to your DNS

Example CNAME records (your tokens will be different):

.. code-block:: text

   Name: abc123._domainkey.aclark.net
   Value: abc123.dkim.amazonses.com

   Name: def456._domainkey.aclark.net
   Value: def456.dkim.amazonses.com

   Name: ghi789._domainkey.aclark.net
   Value: ghi789.dkim.amazonses.com

Quick Start Commands
--------------------

Check current authentication status:

.. code-block:: bash

   ./scripts/check_email_auth.sh

Send test email (after DNS changes):

.. code-block:: bash

   python scripts/test_email_headers.py your-email@gmail.com

Verify DNS records manually:

.. code-block:: bash

   # Check DMARC
   dig TXT _dmarc.aclark.net +short

   # Check SPF
   dig TXT aclark.net +short | grep spf

   # Check DKIM (replace <token> with actual token from AWS)
   dig CNAME <token>._domainkey.aclark.net +short

Timeline
--------

1. **Now**: Add DMARC TXT record to DNS (5 minutes)
2. **Within 1 hour**: Verify domain in AWS SES and add DKIM CNAME records
3. **1-48 hours**: Wait for DNS propagation
4. **After propagation**: Run test script and verify authentication

Expected Results
----------------

After completing all steps:

- SPF: PASS
- DKIM: PASS
- DMARC: PASS
- No more Gmail warnings
- Better email deliverability overall

Documentation
-------------

For detailed information, see:

- :doc:`how-to/fix-gmail-warning` - Complete step-by-step guide
- :doc:`reference/email-dns-records` - DNS records reference
- :doc:`reference/email-utilities` - Email utilities reference
- :doc:`explanation/email-authentication` - Understanding email authentication
- :doc:`how-to/aws-ses-setup` - AWS SES configuration guide

Next Step
---------

**Add the DMARC TXT record to your DNS provider now!** This is the most critical fix.
