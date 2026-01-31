Email Authentication Explained
===============================

This document explains how email authentication works and why it's important for preventing Gmail warnings and improving email deliverability.

The Problem
-----------

Gmail and other email providers show warnings like "Be careful with this message" when emails fail authentication checks. This happens because:

1. Email spoofing and phishing are common security threats
2. Email providers need to verify that emails actually come from who they claim to be from
3. Without proper authentication, your legitimate emails may be marked as suspicious

The Solution: Three Authentication Methods
-------------------------------------------

Modern email authentication uses three complementary technologies:

SPF (Sender Policy Framework)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it does:**

SPF allows domain owners to specify which mail servers are authorized to send email on behalf of their domain.

**How it works:**

1. You publish a TXT record in your DNS listing authorized mail servers
2. When an email arrives, the receiving server checks the DNS record
3. If the sending server is in the authorized list, SPF passes
4. If not, SPF fails and the email may be rejected or marked as spam

**Example SPF record:**

.. code-block:: text

   v=spf1 include:amazonses.com include:_spf.google.com ~all

This says: "Allow AWS SES and Google to send email for this domain, soft-fail everything else"

**Status for aclark.net:** Already configured correctly

DKIM (DomainKeys Identified Mail)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it does:**

DKIM adds a digital signature to your emails that proves they haven't been tampered with and actually came from your domain.

**How it works:**

1. Your mail server signs outgoing emails with a private key
2. You publish the corresponding public key in your DNS
3. Receiving servers use the public key to verify the signature
4. If the signature is valid and matches, DKIM passes

**Why it matters:**

- Proves the email content hasn't been modified in transit
- Confirms the email actually came from your domain
- More secure than SPF alone

**Implementation:**

AWS SES automatically signs emails with DKIM when you verify your domain and enable Easy DKIM. You just need to add the CNAME records AWS provides to your DNS.

**Status for aclark.net:** Need to verify in AWS SES Console

DMARC (Domain-based Message Authentication, Reporting, and Conformance)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**What it does:**

DMARC ties SPF and DKIM together and tells receiving servers what to do when authentication fails.

**How it works:**

1. You publish a DMARC policy in your DNS
2. The policy specifies what to do with emails that fail SPF or DKIM
3. Receiving servers follow your policy (reject, quarantine, or allow)
4. You receive reports about authentication failures

**Why it's critical:**

- **This is the missing piece causing the Gmail warning**
- Without DMARC, even if SPF and DKIM pass, Gmail may still show warnings
- DMARC proves you're actively protecting your domain from spoofing

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

All three authentication methods work together to provide comprehensive email security:

1. **SPF** verifies the sending server is authorized
2. **DKIM** verifies the email content hasn't been tampered with
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

**Your specific issue:**

Your SPF is configured correctly, but DMARC is missing. Even though your emails might be legitimate, Gmail can't verify your domain's authentication policy, so it shows a warning to be safe.

Code Improvements
-----------------

Beyond DNS configuration, the email sending code has been improved to include headers that help with deliverability:

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

These headers don't affect authentication directly, but they improve email deliverability and reduce the chance of being marked as spam.

Implementation
~~~~~~~~~~~~~~

A new email utility module (``aclarknet/email_utils.py``) provides functions that automatically add these headers to all outgoing emails.

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

- :doc:`../how-to/fix-gmail-warning` - Step-by-step guide to fix the warning
- :doc:`../reference/email-dns-records` - Complete DNS records reference
- :doc:`../how-to/aws-ses-setup` - AWS SES configuration guide
