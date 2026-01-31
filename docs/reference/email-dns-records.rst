Email DNS Records Reference
============================

This reference document lists all DNS records required for email authentication with AWS SES.

Domain: aclark.net

Last Updated: 2026-02-01

Critical Records
----------------

DMARC Record (TXT)
~~~~~~~~~~~~~~~~~~

:Record Type: TXT
:Name/Host: ``_dmarc.aclark.net``
:Alternative Name: ``_dmarc`` (some DNS providers)
:Value: ``v=DMARC1; p=quarantine; rua=mailto:aclark@aclark.net; pct=100``
:TTL: 3600
:Status: **MISSING - ADD THIS NOW**

**DMARC Policy Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Parameter
     - Description
   * - ``v=DMARC1``
     - DMARC version 1
   * - ``p=quarantine``
     - Policy: send failed emails to spam (use ``p=reject`` for stricter policy, ``p=none`` for monitoring only)
   * - ``rua=mailto:aclark@aclark.net``
     - Send aggregate reports to this email address
   * - ``pct=100``
     - Apply policy to 100% of emails
   * - ``adkim=s``
     - (Optional) Strict DKIM alignment
   * - ``aspf=s``
     - (Optional) Strict SPF alignment

Already Configured Records
---------------------------

SPF Record (TXT)
~~~~~~~~~~~~~~~~

:Record Type: TXT
:Name/Host: ``aclark.net``
:Alternative Name: ``@`` (root domain on some DNS providers)
:Value: ``v=spf1 include:amazonses.com include:_spf.google.com ~all``
:TTL: 3600
:Status: **CONFIGURED**

**SPF Policy Parameters:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Parameter
     - Description
   * - ``v=spf1``
     - SPF version 1
   * - ``include:amazonses.com``
     - Allow AWS SES to send email
   * - ``include:_spf.google.com``
     - Allow Google to send email
   * - ``~all``
     - Soft fail for all other senders

Records from AWS SES Console
-----------------------------

DKIM Records (3 CNAME records)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These records must be obtained from the AWS SES Console.

**How to get DKIM tokens:**

1. Go to https://console.aws.amazon.com/ses/
2. Navigate to Configuration → Verified identities
3. If ``aclark.net`` is listed:

   - Click on it
   - Look for "DKIM" section
   - Copy the 3 CNAME records

4. If ``aclark.net`` is NOT listed:

   - Click "Create identity"
   - Select "Domain"
   - Enter ``aclark.net``
   - Enable "Easy DKIM"
   - AWS will show you 3 CNAME records

**Example format (your actual tokens will be different):**

Record 1:

:Record Type: CNAME
:Name/Host: ``abc123xyz._domainkey.aclark.net``
:Value: ``abc123xyz.dkim.amazonses.com``
:TTL: 3600

Record 2:

:Record Type: CNAME
:Name/Host: ``def456uvw._domainkey.aclark.net``
:Value: ``def456uvw.dkim.amazonses.com``
:TTL: 3600

Record 3:

:Record Type: CNAME
:Name/Host: ``ghi789rst._domainkey.aclark.net``
:Value: ``ghi789rst.dkim.amazonses.com``
:TTL: 3600

:Status: **UNKNOWN - CHECK AWS SES CONSOLE**

DNS Provider-Specific Notes
----------------------------

GoDaddy
~~~~~~~

- For root domain records, use ``@`` as the host
- For ``_dmarc``, enter ``_dmarc`` (without the domain)
- For DKIM, enter the full token (e.g., ``abc123xyz._domainkey``)

Cloudflare
~~~~~~~~~~

- For root domain, use ``@``
- For ``_dmarc``, enter ``_dmarc``
- For DKIM, enter the full token
- Make sure "Proxy status" is set to "DNS only" (gray cloud icon)

Namecheap
~~~~~~~~~

- For root domain, use ``@``
- For ``_dmarc``, enter ``_dmarc``
- For DKIM, enter the full token

Route 53 (AWS)
~~~~~~~~~~~~~~

- Enter full domain names (e.g., ``_dmarc.aclark.net``)
- TXT record values should be in quotes
- CNAME values should NOT be in quotes

Verification Commands
---------------------

After adding records, verify with these commands:

Check DMARC
~~~~~~~~~~~

.. code-block:: bash

   dig TXT _dmarc.aclark.net +short

Check SPF
~~~~~~~~~

.. code-block:: bash

   dig TXT aclark.net +short | grep spf

Check DKIM
~~~~~~~~~~

Replace ``<token>`` with actual token from AWS:

.. code-block:: bash

   dig CNAME <token>._domainkey.aclark.net +short

Automated Script
~~~~~~~~~~~~~~~~

.. code-block:: bash

   ./scripts/check_email_auth.sh
