Email Authentication Explained
===============================

This document explains how email authentication prevents Gmail warnings
and improves deliverability.

The Problem
-----------

Gmail and other providers show warnings like "Be careful with this
message" when emails fail authentication checks. Without proper
authentication, legitimate mail may be treated as suspicious.

The Solution: Three Authentication Methods
-------------------------------------------

Modern email authentication uses three complementary technologies:

SPF (Sender Policy Framework)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it does:**

SPF lets domain owners specify which mail servers may send email for the
domain.

**How it works:**

1. You publish a TXT record in DNS listing authorized mail servers
2. When an email arrives, the receiving server checks the DNS record
3. If the sending server is authorized, SPF passes
4. If not, SPF fails and the email may be rejected or marked as spam

**Example SPF record:**

.. code-block:: text

   v=spf1 include:amazonses.com include:_spf.google.com ~all

This says: "Allow AWS SES and Google to send email for this domain,
soft-fail everything else"

**Status for aclark.net:** Already configured correctly

DKIM (DomainKeys Identified Mail)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it does:**

DKIM adds a digital signature that proves a message came from your domain
and was not modified in transit.

**How it works:**

1. Your mail server signs outgoing emails with a private key
2. You publish the corresponding public key in DNS
3. Receiving servers use the public key to verify the signature
4. If the signature is valid and matches, DKIM passes

**Why it matters:**

- Proves the email content has not been modified in transit
- Confirms the email came from your domain
- Provides stronger assurance than SPF alone

**Implementation:**

AWS SES automatically signs emails with DKIM when you verify your domain
and enable Easy DKIM. You only need to add the CNAME records AWS
provides to your DNS.

**Status for aclark.net:** Need to verify in AWS SES Console

DMARC (Domain-based Message Authentication, Reporting, and Conformance)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it does:**

DMARC ties SPF and DKIM together and tells receiving servers what to do
when authentication fails.

**How it works:**

1. You publish a DMARC policy in DNS
2. The policy specifies what to do with emails that fail SPF or DKIM
3. Receiving servers follow your policy (reject, quarantine, or allow)
4. You receive reports about authentication failures

**Why it's critical:**

- **This is the missing piece causing the Gmail warning**
- Without DMARC, Gmail may still show warnings even if SPF and DKIM pass
- DMARC proves you are actively protecting your domain from spoofing

**DMARC policies:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Policy
     - Effect
   * - ``p=none``
     - Monitor only - don't reject or quarantine failed emails (good for testing)
   * - ``p=quarantine``
     - Send failed emails to spam folder (recommended for production)
   * - ``p=reject``
     - Reject failed emails entirely (strictest policy)

**Status for aclark.net:** **MISSING - This is causing the Gmail warning**

How They Work Together
----------------------

1. **SPF** verifies the sending server is authorized
2. **DKIM** verifies the email content has not been tampered with
3. **DMARC** ties them together and enforces a policy

**Authentication flow:**

.. code-block:: text

   Email sent from aclark@aclark.net
         ↓
   SPF Check: Is the sending server authorized?
         ↓
   DKIM Check: Is the signature valid?
         ↓
   DMARC Check: Do SPF and DKIM align with the From domain?
         ↓
   All pass? → Email delivered to inbox
   Any fail? → Follow DMARC policy (quarantine/reject)

Why Gmail Shows Warnings
-------------------------

Gmail shows "Be careful with this message" when:

1. **DMARC is missing** (most common - this is your issue)
2. SPF fails
3. DKIM fails
4. DMARC policy fails (SPF and DKIM don't align)
5. The sending domain has a poor reputation

Your SPF is configured correctly, but DMARC is missing. Even if the mail
is legitimate, Gmail cannot verify your domain's policy, so it warns the
recipient.

Code Improvements
-----------------

Beyond DNS configuration, the email sending code has been improved to
include headers that help with deliverability:

Email Headers Added
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Header
     - Purpose
   * - ``Reply-To``
     - Specifies where replies should go
   * - ``X-Mailer``
     - Identifies the sending application
   * - ``X-Auto-Response-Suppress``
     - Prevents auto-reply loops
   * - ``Precedence: bulk``
     - Indicates automated mail

These headers do not affect authentication directly, but they improve
deliverability and reduce the chance of being marked as spam.

Implementation
~~~~~~~~~~~~~~

A new email utility module (``aclarknet/email_utils.py``) provides
functions that automatically add these headers to all outgoing emails.

Timeline for Fix
----------------

1. **Add DMARC record** (5 minutes) - Critical first step
2. **Verify domain in AWS SES** (15 minutes) - Get DKIM tokens
3. **Add DKIM records** (5 minutes) - Add 3 CNAME records to DNS
4. **Wait for DNS propagation** (1-48 hours) - Usually much faster
5. **Test authentication** (5 minutes) - Verify all checks pass
6. **Gmail warning disappears** - Success!

Expected Results
----------------

After completing all steps, emails from aclark.net will:

- Pass all three authentication checks (SPF, DKIM, DMARC)
- No longer show Gmail warnings
- Have better deliverability overall
- Be less likely to end up in spam folders
- Build domain reputation over time

See Also
--------

- :doc:`fix-gmail-warning` - Step-by-step guide to fix the warning
- :doc:`email-dns-records` - Complete DNS records reference
- :doc:`aws-ses-setup` - AWS SES configuration guide
