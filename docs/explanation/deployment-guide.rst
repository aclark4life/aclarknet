Deployment Guide for aclarknet
==============================

This guide provides instructions for deploying the aclarknet
Django/Wagtail application to a production server running Amazon Linux
2023 with nginx.

Server Requirements
-------------------

- Amazon Linux 2023
- Python 3.13 or higher
- MongoDB (local or remote instance)
- nginx (already installed and configured with HTTPS)
- Git
- Node.js (for building frontend assets)
- systemd (for service management)

Prerequisites
-------------

1. SSH access to the server (aclark.net)
2. sudo/root access
3. MongoDB instance available
4. SSL certificates configured in nginx
5. DNS configured to point aclark.net, www.aclark.net, and m.aclark.net
   to your server

Initial Deployment
------------------

1. Prepare the Server
~~~~~~~~~~~~~~~~~~~~~

SSH into your server:

.. code:: bash

   ssh user@aclark.net

Install required system packages:

.. code:: bash

   sudo dnf update -y
   sudo dnf install -y python3 python3-pip git mongodb-org nodejs npm

Ensure nginx is installed and running:

.. code:: bash

   sudo systemctl status nginx

2. Clone the Repository and Run Deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Option A: Using ``just`` (Recommended)**

.. code:: bash

   # Clone the repository
   git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy
   cd /tmp/aclarknet-deploy

   # Install just if not already installed
   curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

   # Run initial deployment
   just deploy-initial
   # or use the short alias: just di

**Option B: Using the deployment script directly**

.. code:: bash

   # Clone the repository to a temporary location
   git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy
   cd /tmp/aclarknet-deploy

   # Copy deployment script to a convenient location
   sudo cp deployment/deploy.sh /usr/local/bin/aclarknet-deploy
   sudo chmod +x /usr/local/bin/aclarknet-deploy

   # Run initial deployment
   sudo aclarknet-deploy --initial

3. Configure Environment Variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit the environment file with your production settings:

.. code:: bash

   sudo nano /srv/aclarknet/.env

**Important settings to configure:**

.. code:: bash

   # Generate a secure secret key (you can use: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
   DJANGO_SECRET_KEY=your-actual-secret-key-here

   # Set allowed hosts
   DJANGO_ALLOWED_HOSTS=aclark.net,www.aclark.net,m.aclark.net

   # Set CSRF trusted origins
   DJANGO_CSRF_TRUSTED_ORIGINS=https://aclark.net,https://www.aclark.net,https://m.aclark.net

   # MongoDB configuration (adjust if using remote MongoDB)
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=aclarknet

   # Email settings - See docs/aws_ses_setup.md for AWS SES configuration
   # Option 1: AWS SES (recommended for production)
   USE_SES=True
   AWS_ACCESS_KEY_ID=your-aws-access-key-id
   AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
   AWS_SES_REGION_NAME=us-east-1

   # Option 2: SMTP (alternative)
   # USE_SES=False
   # EMAIL_HOST=smtp.example.com
   # EMAIL_PORT=587
   # EMAIL_USE_TLS=True
   # EMAIL_HOST_USER=your-email@example.com
   # EMAIL_HOST_PASSWORD=your-email-password

**Note**: For detailed AWS SES setup instructions, see `AWS SES Setup
Guide <aws_ses_setup.md>`__.

4. Configure nginx
~~~~~~~~~~~~~~~~~~

Edit the nginx configuration to add your SSL certificate paths:

.. code:: bash

   sudo nano /etc/nginx/conf.d/aclarknet.conf

Update these lines with your actual certificate paths:

.. code:: nginx

   ssl_certificate /path/to/your/fullchain.pem;
   ssl_certificate_key /path/to/your/privkey.pem;

Test nginx configuration and reload:

.. code:: bash

   sudo nginx -t
   sudo systemctl reload nginx

5. Create Django Superuser
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python manage.py createsuperuser

6. Setup The Lounge IRC Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create users for The Lounge:

.. code:: bash

   cd /srv/aclarknet/lounge
   sudo -u nginx node_modules/.bin/thelounge add <username>

You’ll be prompted to set a password for the user. Repeat for each user
you want to create.

7. Verify Deployment
~~~~~~~~~~~~~~~~~~~~

1. Check service status:

.. code:: bash

   sudo systemctl status aclarknet.service
   sudo systemctl status thelounge.service

2. Check logs if there are issues:

.. code:: bash

   sudo journalctl -u aclarknet.service -n 50
   sudo journalctl -u thelounge.service -n 50
   sudo tail -f /srv/aclarknet/logs/gunicorn-error.log
   sudo tail -f /srv/aclarknet/logs/django.log

3. Visit your site:

- Main site: https://aclark.net
- Admin: https://aclark.net/admin/
- Wagtail Admin: https://aclark.net/wagtail/
- The Lounge IRC: https://aclark.net/lounge/

Subsequent Deployments
----------------------

For updating the application after the initial deployment:

**Option A: Using ``just`` (Recommended)**

.. code:: bash

   # Deploy updates
   just deploy
   # or use the short alias: just dp

**Option B: Using the deployment script directly**

.. code:: bash

   sudo aclarknet-deploy

This will: 1. Pull the latest code from the repository 2. Install any
new dependencies 3. Build frontend assets 4. Collect static files 5. Run
database migrations 6. Restart the application

Useful ``just`` Commands
------------------------

Once deployed, you can use these commands for common tasks:

.. code:: bash

   # Check service status
   just deploy-status  # or: just ds

   # View recent logs
   just deploy-logs  # or: just dl

   # Restart the service
   just deploy-restart  # or: just dr

   # Build production assets locally (before deploying)
   just build-prod  # or: just bp

Manual Deployment Steps
-----------------------

If you prefer to deploy manually or need to troubleshoot:

Update Code
~~~~~~~~~~~

.. code:: bash

   cd /srv/aclarknet/repo
   sudo -u nginx git pull origin main

Install Dependencies
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   cd /srv/aclarknet/repo
   sudo -u nginx /srv/aclarknet/venv/bin/pip install -e .

Build Frontend
~~~~~~~~~~~~~~

.. code:: bash

   cd /srv/aclarknet/repo
   sudo -u nginx npm install
   sudo -u nginx npm run build

Collect Static Files
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   cd /srv/aclarknet/repo
   sudo -u nginx /srv/aclarknet/venv/bin/python manage.py collectstatic --noinput

Run Migrations
~~~~~~~~~~~~~~

.. code:: bash

   cd /srv/aclarknet/repo
   sudo -u nginx /srv/aclarknet/venv/bin/python manage.py migrate

Restart Services
~~~~~~~~~~~~~~~~

.. code:: bash

   sudo systemctl restart aclarknet.service
   sudo systemctl restart thelounge.service

The Lounge IRC Client
---------------------

The Lounge is a self-hosted web IRC client that runs alongside the main
Django application.

Configuration
~~~~~~~~~~~~~

The Lounge configuration is located at
``/srv/aclarknet/lounge/.thelounge/config.js``.

Key configuration settings: - **Mode**: Private (requires user
authentication) - **Port**: 9000 (localhost only, proxied through nginx)
- **Reverse Proxy**: Enabled - **Reverse Proxy Path**: ``/lounge/``
(required for subpath deployment) - **Default Network**: Libera.Chat

**Important**: The ``reverseProxyPath`` setting in the config file must
be set to ``/lounge/`` to match the nginx proxy path. This ensures all
assets use the correct path when accessed through
https://aclark.net/lounge/.

User Management
~~~~~~~~~~~~~~~

.. code:: bash

   # Create a new user
   cd /srv/aclarknet/lounge
   sudo -u nginx node_modules/.bin/thelounge add <username>

   # List all users
   sudo -u nginx node_modules/.bin/thelounge list

   # Remove a user
   sudo -u nginx node_modules/.bin/thelounge remove <username>

   # Reset user password
   sudo -u nginx node_modules/.bin/thelounge reset <username>

Service Management
~~~~~~~~~~~~~~~~~~

.. code:: bash

   # Check status
   sudo systemctl status thelounge.service

   # Start/stop/restart
   sudo systemctl start thelounge.service
   sudo systemctl stop thelounge.service
   sudo systemctl restart thelounge.service

   # View logs
   sudo journalctl -u thelounge.service -f

Accessing The Lounge
~~~~~~~~~~~~~~~~~~~~

Once deployed, access The Lounge at: **https://aclark.net/lounge/**

Log in with the username and password you created using the
``thelounge add`` command.

Troubleshooting
---------------

Service Won’t Start
~~~~~~~~~~~~~~~~~~~

Check the service logs:

.. code:: bash

   sudo journalctl -u aclarknet.service -n 100

Check gunicorn logs:

.. code:: bash

   sudo tail -n 100 /srv/aclarknet/logs/gunicorn-error.log

Static Files Not Loading
~~~~~~~~~~~~~~~~~~~~~~~~

1. Verify static files are collected:

.. code:: bash

   ls -la /srv/aclarknet/static/

2. Check nginx configuration:

.. code:: bash

   sudo nginx -t

3. Check file permissions:

.. code:: bash

   sudo chown -R nginx:nginx /srv/aclarknet/static/

Database Connection Issues
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Check MongoDB is running:

.. code:: bash

   sudo systemctl status mongod

2. Verify MongoDB connection string in ``/srv/aclarknet/.env``

3. Test connection:

.. code:: bash

   mongosh $MONGODB_URI

502 Bad Gateway
~~~~~~~~~~~~~~~

This usually means gunicorn isn’t running or the socket permissions are
wrong:

1. Check gunicorn service:

.. code:: bash

   sudo systemctl status aclarknet.service

2. Check socket file:

.. code:: bash

   ls -la /srv/aclarknet/aclarknet.sock

3. Restart service:

.. code:: bash

   sudo systemctl restart aclarknet.service

Monitoring
----------

Check Service Status
~~~~~~~~~~~~~~~~~~~~

.. code:: bash

   sudo systemctl status aclarknet.service

View Live Logs
~~~~~~~~~~~~~~

.. code:: bash

   # Gunicorn access log
   sudo tail -f /srv/aclarknet/logs/gunicorn-access.log

   # Gunicorn error log
   sudo tail -f /srv/aclarknet/logs/gunicorn-error.log

   # Django application log
   sudo tail -f /srv/aclarknet/logs/django.log

   # nginx access log
   sudo tail -f /srv/aclarknet/logs/nginx-access.log

   # nginx error log
   sudo tail -f /srv/aclarknet/logs/nginx-error.log

   # systemd service log
   sudo journalctl -u aclarknet.service -f

Security Considerations
-----------------------

1. **Keep SECRET_KEY secret**: Never commit it to version control
2. **Use strong passwords**: For database and Django admin
3. **Regular updates**: Keep system packages and Python dependencies
   updated
4. **Firewall**: Ensure only necessary ports are open (80, 443, 22)
5. **HTTPS only**: The configuration forces HTTPS redirects
6. **File permissions**: Ensure .env file is only readable by nginx user
7. **Regular backups**: Backup your MongoDB database regularly

Backup and Restore
------------------

Backup MongoDB
~~~~~~~~~~~~~~

.. code:: bash

   mongodump --uri="mongodb://localhost:27017/aclarknet" --out=/backup/mongodb/$(date +%Y%m%d)

Restore MongoDB
~~~~~~~~~~~~~~~

.. code:: bash

   mongorestore --uri="mongodb://localhost:27017/aclarknet" /backup/mongodb/20240101/aclarknet/

Backup Media Files
~~~~~~~~~~~~~~~~~~

.. code:: bash

   tar -czf /backup/media-$(date +%Y%m%d).tar.gz /srv/aclarknet/media/

Additional Resources
--------------------

- `Django Deployment
  Checklist <https://docs.djangoproject.com/en/stable/howto/deployment/checklist/>`__
- `Wagtail Deployment
  Guide <https://docs.wagtail.org/en/stable/advanced_topics/deploying.html>`__
- `Gunicorn Documentation <https://docs.gunicorn.org/>`__
- `nginx Documentation <https://nginx.org/en/docs/>`__
