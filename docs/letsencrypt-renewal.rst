Automating Let's Encrypt Certificate Renewal
=============================================

This guide documents how the ``aclark.net`` production server automatically
renews its Let's Encrypt SSL certificate before it expires.

Overview
--------

The server (Amazon Linux 2023, EC2) uses ``certbot`` to manage the
Let's Encrypt certificate for ``aclark.net`` and ``www.aclark.net``.
Renewal is automated with a **systemd timer** rather than cron, since
Amazon Linux 2023 does not ship a cron daemon by default.

The ``certbot`` package installs two systemd units:

* ``certbot-renew.timer`` — schedules renewal checks
* ``certbot-renew.service`` — runs ``certbot renew`` when triggered

By default, ``certbot renew`` only renews a certificate once it is
within **~30 days of expiry** (certbot's built-in default). This
threshold is not configurable via a simple flag; it is handled
internally by certbot for every certificate it manages.

Checking Current Status
------------------------

SSH into the server and inspect the certificate and timer:

.. code:: bash

   ssh aclark.net

   # Certificate details and expiry date
   sudo certbot certificates

   # Timer schedule and status
   systemctl list-timers certbot-renew.timer
   systemctl status certbot-renew.timer

Enabling the Renewal Timer
---------------------------

The timer ships disabled. Enable and start it so renewal checks run
automatically going forward:

.. code:: bash

   sudo systemctl enable --now certbot-renew.timer

This runs ``certbot renew`` twice daily (``00:00`` and ``12:00`` UTC),
each with up to a 12-hour randomized delay (``RandomizedDelaySec=12hours``)
to avoid load spikes across Let's Encrypt's infrastructure. Certificates
are only actually renewed when within the ~30-day expiry window, so most
runs are no-ops.

Manually Renewing a Certificate
---------------------------------

If a certificate has already expired or you want to force an immediate
renewal without waiting for the random delay:

.. code:: bash

   sudo certbot renew --cert-name aclark.net --non-interactive --no-random-sleep-on-renew

``--no-random-sleep-on-renew`` skips certbot's built-in randomized
delay, which otherwise can add several minutes before renewal starts.

Verifying Renewal
------------------

After a renewal (automatic or manual), confirm the new expiry date:

.. code:: bash

   sudo certbot certificates

Look for ``Expiry Date`` and confirm it is roughly 90 days out, and that
nginx was reloaded (certbot's nginx hook does this automatically).

Troubleshooting
----------------

Timer shows ``inactive (dead)``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The timer was never enabled. Run:

.. code:: bash

   sudo systemctl enable --now certbot-renew.timer

Certificate still expired after a timer run
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check the service logs:

.. code:: bash

   journalctl -u certbot-renew.service --no-pager -n 50

Renewal seems stuck / slow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Manual (non-timer) invocations of ``certbot renew`` include a random
delay of up to several minutes by default. Use
``--no-random-sleep-on-renew`` to skip it for one-off manual runs.

See Also
--------

* `Certbot documentation <https://eff-certbot.readthedocs.io/>`__
* :doc:`ec2-iam-role-setup`
