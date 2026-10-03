Quick Deployment Guide
======================

Quick reference for deploying aclarknet to aclark.net, including
``www.aclark.net`` and ``m.aclark.net``.

Using ``just`` Commands (Recommended)
-------------------------------------

.. code:: bash

   # Initial deployment
   just deploy-initial  # or: just di

   # Update deployment (local, requires /srv write access)
   just deploy  # or: just dp

   # Update deployment remotely via SSH (recommended from dev machine)
   just deploy-remote  # or: just dpr

   # Check service status
   just deploy-status  # or: just ds

   # View logs
   just deploy-logs  # or: just dl

   # Restart service
   just deploy-restart  # or: just dr

Deploying via GitHub Actions
----------------------------

Deployment can also be triggered from GitHub Actions via the manual-only
**Deploy to Production** workflow:

.. code:: bash

   gh workflow run deploy.yml --repo aclark4life/aclarknet

You can also trigger it from the Actions tab in the GitHub UI. The
workflow is ``workflow_dispatch``-only, so deploys are always explicit.
It runs the same ``deployment/deploy.sh`` script over SSH as
``just deploy-remote``, using the ``DEPLOY_SSH_KEY`` repository secret.

Manual Deployment
-----------------

Initial Deployment (First Time)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   # 1. SSH to server
   ssh user@aclark.net

   # 2. Install system dependencies
   sudo dnf update -y
   sudo dnf install -y python3 python3-pip git mongodb-org nodejs npm

   # 3. Start MongoDB
   sudo systemctl start mongod
   sudo systemctl enable mongod

   # 4. Clone and deploy
   git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy
   cd /tmp/aclarknet-deploy
   sudo cp deployment/deploy.sh /usr/local/bin/aclarknet-deploy
   sudo chmod +x /usr/local/bin/aclarknet-deploy
   sudo /usr/local/bin/aclarknet-deploy --initial

   # 5. Configure environment
   sudo nano /srv/aclarknet/.env
   # Update: DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, DJANGO_CSRF_TRUSTED_ORIGINS

   # 6. Obtain SSL certificates for all domains
   sudo dnf install certbot python3-certbot-nginx
   sudo certbot --nginx -d aclark.net -d www.aclark.net -d m.aclark.net

   # 7. Test and reload nginx
   sudo nginx -t
   sudo systemctl reload nginx

   # 8. Create superuser
   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python manage.py createsuperuser

   # 9. Create The Lounge users
   cd /srv/aclarknet/lounge
   sudo -u nginx node_modules/.bin/thelounge add <username>

   # 10. Check status
   sudo systemctl status aclarknet.service
   sudo systemctl status thelounge.service

Subsequent Deployments
----------------------

.. code:: bash

   # SSH to server
   ssh user@aclark.net

   # Run deployment script
   sudo aclarknet-deploy

Quick Checks
------------

.. code:: bash

   # Check service status
   sudo systemctl status aclarknet.service
   sudo systemctl status thelounge.service

   # View logs
   sudo journalctl -u aclarknet.service -n 50
   sudo journalctl -u thelounge.service -n 50
   sudo tail -f /srv/aclarknet/logs/gunicorn-error.log

   # Restart services
   sudo systemctl restart aclarknet.service
   sudo systemctl restart thelounge.service

The Lounge IRC Client
---------------------

The Lounge is available at **https://aclark.net/lounge/**.

``/srv/aclarknet/lounge/.thelounge/config.js`` must have
``reverseProxyPath: "/lounge/"`` set for nginx reverse proxying.

.. code:: bash

   # Create a user
   cd /srv/aclarknet/lounge
   sudo -u nginx node_modules/.bin/thelounge add <username>

   # List users
   sudo -u nginx node_modules/.bin/thelounge list

   # Check service
   sudo systemctl status thelounge.service

   # If The Lounge is not working, verify the configuration:
   grep reverseProxyPath /srv/aclarknet/lounge/.thelounge/config.js
   # Should show: reverseProxyPath: "/lounge/",

File Locations
--------------

- Application: ``/srv/aclarknet``
- Virtual Environment: ``/srv/aclarknet/.venv``
- Environment Config: ``/srv/aclarknet/.env``
- Logs: ``/srv/aclarknet/logs/``
- Static Files: ``/srv/aclarknet/static/``
- Media Files: ``/srv/aclarknet/media/``
- The Lounge: ``/srv/aclarknet/lounge``
- Systemd Services: ``/etc/systemd/system/aclarknet.service``,
  ``/etc/systemd/system/thelounge.service``
- nginx Config: ``/etc/nginx/conf.d/aclarknet.conf``

For more detail, see `Deployment Guide <deployment_guide>`__
