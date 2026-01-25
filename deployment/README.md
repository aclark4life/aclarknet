# Deployment Guide for aclarknet

This guide explains how to deploy the aclarknet Django application to a production server.

## Quick Reference

- **[deploy.sh](deploy.sh)** - Automated deployment script
- **[.env.example](.env.example)** - Environment variables template

## Deployment Structure

The deployment uses the following structure:

```
/srv/aclarknet/
├── .venv/                    # Python virtual environment
├── .env                      # Environment variables (not in git)
├── logs/                     # Application logs
├── static/                   # Collected static files
├── media/                    # User-uploaded media files
├── manage.py                 # Django management script
├── aclarknet/               # Main Django project
├── home/                    # Home app
├── db/                      # Database app
├── cms/                     # CMS app
├── search/                  # Search app
├── siteuser/                # Site user app
├── lounge/                  # The Lounge IRC client
│   ├── .thelounge/          # The Lounge configuration
│   └── node_modules/        # Node.js dependencies
├── frontend/                # Frontend assets
├── deployment/              # Deployment configuration
└── ...                      # Other project files
```

## Key Changes from Previous Setup

1. **Virtual Environment Location**: Changed from `/srv/aclarknet/venv` to `/srv/aclarknet/.venv`
2. **Project Location**: Django project files are now directly in `/srv/aclarknet` instead of `/srv/aclarknet/repo`
3. **PYTHONPATH**: Added explicit PYTHONPATH environment variable in systemd service to ensure all Django apps (including `home`) can be imported correctly

## Prerequisites

### System Requirements

- Amazon Linux 2023 (or similar RHEL-based distribution)
- Python 3.13 or later
- Node.js (for building frontend assets)
- MongoDB (running locally or accessible via network)
- nginx web server
- systemd (for service management)

### Installation Commands (Amazon Linux 2023)

```bash
# Install Python 3.13
sudo dnf install python3.13 python3.13-pip python3.13-devel

# Install Node.js (use nvm or dnf)
sudo dnf install nodejs npm

# Install nginx
sudo dnf install nginx

# Install MongoDB (if running locally)
sudo dnf install mongodb-org

# Install rsync (usually pre-installed)
sudo dnf install rsync
```

## Initial Deployment

1. **Clone and Run Deployment Script**

   ```bash
   # Clone the repository to a temporary location
   git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy

   # Copy the deployment script
   sudo cp /tmp/aclarknet-deploy/deployment/deploy.sh /tmp/
   sudo chmod +x /tmp/deploy.sh

   # Run initial deployment
   sudo /tmp/deploy.sh --initial
   ```

2. **Configure Environment Variables**

   Edit `/srv/aclarknet/.env` with your production settings:

   ```bash
   sudo -e /srv/aclarknet/.env
   ```

   Important variables to set:
   - `DJANGO_SECRET_KEY`: Generate a secure secret key
   - `DJANGO_ALLOWED_HOSTS`: Your domain name(s)
   - `DJANGO_CSRF_TRUSTED_ORIGINS`: Your HTTPS URLs
   - `MONGODB_URI`: MongoDB connection string (if not localhost)
   - `MONGODB_DB`: Database name

3. **Configure SSL Certificates**

   Update nginx configuration with your SSL certificate paths:

   ```bash
   sudo -e /etc/nginx/conf.d/aclarknet.conf
   ```

   Or use Let's Encrypt to obtain certificates for all domains:

   ```bash
   sudo dnf install certbot python3-certbot-nginx
   sudo certbot --nginx -d aclark.net -d www.aclark.net -d m.aclark.net
   ```

   This will obtain a single certificate that covers all three domains (aclark.net, www.aclark.net, and m.aclark.net).

4. **Test and Start Services**

   ```bash
   # Test nginx configuration
   sudo nginx -t

   # Reload nginx
   sudo systemctl reload nginx

   # Check aclarknet service status
   sudo systemctl status aclarknet.service

   # View logs if needed
   sudo journalctl -u aclarknet.service -n 50
   ```

5. **Create Django Superuser**

   ```bash
   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python manage.py createsuperuser
   ```

## Updating the Application

To update the application with new code:

```bash
sudo /tmp/deploy.sh
```

This will:
- Clone the latest code from the repository
- Sync files to `/srv/aclarknet` (preserving logs, static, media, and .env)
- Update Python dependencies
- Build frontend assets
- Collect static files
- Run database migrations
- Restart the gunicorn service

## Service Management

### Start/Stop/Restart Services

```bash
# Start the application
sudo systemctl start aclarknet.service

# Stop the application
sudo systemctl stop aclarknet.service

# Restart the application
sudo systemctl restart aclarknet.service

# Check service status
sudo systemctl status aclarknet.service
```

### View Logs

```bash
# Gunicorn access logs
sudo tail -f /srv/aclarknet/logs/gunicorn-access.log

# Gunicorn error logs
sudo tail -f /srv/aclarknet/logs/gunicorn-error.log

# Django application logs
sudo tail -f /srv/aclarknet/logs/django.log

# Systemd service logs
sudo journalctl -u aclarknet.service -f

# Nginx logs
sudo tail -f /srv/aclarknet/logs/nginx-access.log
sudo tail -f /srv/aclarknet/logs/nginx-error.log
```

## The Lounge IRC Client

The Lounge is a self-hosted web IRC client that runs as a separate service alongside the main Django application.

### Service Management

```bash
# Start The Lounge
sudo systemctl start thelounge.service

# Stop The Lounge
sudo systemctl stop thelounge.service

# Restart The Lounge
sudo systemctl restart thelounge.service

# Check service status
sudo systemctl status thelounge.service

# View logs
sudo journalctl -u thelounge.service -f
```

### User Management

The Lounge runs in private mode, which requires user accounts. To create users:

```bash
# Create a new user
cd /srv/aclarknet/lounge
sudo -u nginx node_modules/.bin/thelounge add <username>

# List users
sudo -u nginx node_modules/.bin/thelounge list

# Remove a user
sudo -u nginx node_modules/.bin/thelounge remove <username>

# Reset a user's password
sudo -u nginx node_modules/.bin/thelounge reset <username>
```

### Accessing The Lounge

Once deployed, The Lounge is accessible at:
- **URL**: https://aclark.net/lounge/
- **Port**: Runs on port 9000 (proxied through nginx)

### Configuration

The Lounge configuration is located at:
- `/srv/aclarknet/lounge/.thelounge/config.js`

Key settings:
- **Private mode**: Enabled (requires user authentication)
- **Reverse proxy**: Enabled (for nginx integration)
- **Reverse proxy path**: `/lounge/` (required for subpath deployment)
- **Default network**: Libera.Chat IRC network
- **Port**: 9000 (localhost only)

To modify configuration:
1. Edit the config file
2. Restart the service: `sudo systemctl restart thelounge.service`

**Important**: The `reverseProxyPath` setting must be set to `/lounge/` to match the nginx proxy configuration. Without this setting, The Lounge will not work properly when accessed through the reverse proxy at https://aclark.net/lounge/.

## Troubleshooting

### Service Won't Start

1. Check the service status and logs:
   ```bash
   sudo systemctl status aclarknet.service
   sudo journalctl -u aclarknet.service -n 50
   ```

2. Common issues:
   - Missing or invalid `.env` file
   - Incorrect file permissions
   - MongoDB not running
   - Python dependencies not installed

### Import Errors (e.g., "home" cannot be imported)

The systemd service now includes `Environment="PYTHONPATH=/srv/aclarknet"` to ensure all Django apps can be imported. If you still experience import issues:

1. Verify the working directory is correct:
   ```bash
   grep WorkingDirectory /etc/systemd/system/aclarknet.service
   # Should show: WorkingDirectory=/srv/aclarknet
   ```

2. Verify PYTHONPATH is set:
   ```bash
   grep PYTHONPATH /etc/systemd/system/aclarknet.service
   # Should show: Environment="PYTHONPATH=/srv/aclarknet"
   ```

3. Test imports manually:
   ```bash
   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python -c "import home; print('Import successful')"
   ```

### Permission Errors

Ensure all files are owned by the nginx user:

```bash
sudo chown -R nginx:nginx /srv/aclarknet
```

### Nginx Cannot Connect to Gunicorn

If you see errors like `connect() to 127.0.0.1:8000 failed` or connection refused:

1. Check if the gunicorn service is running:
   ```bash
   sudo systemctl status aclarknet.service
   ```

2. Verify gunicorn is listening on port 8000:
   ```bash
   sudo netstat -tulpn | grep :8000
   # or
   sudo ss -tulpn | grep :8000
   ```

3. Check if port 8000 is already in use by another process:
   ```bash
   sudo lsof -i :8000
   ```

4. Restart the service:
   ```bash
   sudo systemctl restart aclarknet.service
   ```

### Static Files Not Loading

1. Collect static files again:
   ```bash
   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python manage.py collectstatic --noinput
   ```

2. Verify nginx can read the static directory:
   ```bash
   sudo ls -la /srv/aclarknet/static/
   ```

## File Permissions

The deployment uses the `nginx` user and group for running the application. Important directories and their permissions:

- `/srv/aclarknet`: Owned by `nginx:nginx`
- `/srv/aclarknet/.venv`: Owned by `nginx:nginx`
- `/srv/aclarknet/.env`: Owned by `nginx:nginx`, mode `600` (read/write for owner only)
- `/srv/aclarknet/logs`: Owned by `nginx:nginx`
- `/srv/aclarknet/static`: Owned by `nginx:nginx`
- `/srv/aclarknet/media`: Owned by `nginx:nginx`

## Security Notes

1. **Secret Key**: Always use a unique, randomly generated secret key in production
2. **HTTPS Only**: The nginx configuration redirects all HTTP traffic to HTTPS
3. **Environment Variables**: The `.env` file contains sensitive information and should have mode `600`
4. **Database**: Ensure MongoDB is configured with authentication if accessible over the network
5. **Firewall**: Configure firewall to only allow necessary ports (80, 443)

## Architecture

### Components

1. **nginx**: Reverse proxy, handles SSL termination, serves static/media files
2. **gunicorn**: WSGI server, runs Django application
3. **systemd**: Service manager, manages gunicorn process lifecycle
4. **MongoDB**: Database backend
5. **Django**: Web application framework
6. **Wagtail**: CMS framework

### Request Flow

```
Client Request (HTTPS)
  → nginx (port 443)
    → Static files: Served directly from /srv/aclarknet/static/
    → Media files: Served directly from /srv/aclarknet/media/
    → Application requests: Proxied to gunicorn via TCP
      → TCP connection (127.0.0.1:8000)
        → gunicorn (managed by systemd)
          → Django/Wagtail application
            → MongoDB database
```

**Note**: Gunicorn binds to 127.0.0.1:8000 (localhost only) for security, which nginx proxies to via TCP connection.

## Development vs Production

### Development
- Uses `aclarknet.settings.dev`
- DEBUG = True
- SQLite can be used for local development
- Run with: `python manage.py runserver`

### Production
- Uses `aclarknet.settings.production`
- DEBUG = False
- MongoDB required
- HTTPS enforced
- Static files served by nginx
- Run with: systemd service (gunicorn)

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [nginx Documentation](https://nginx.org/en/docs/)
- [Wagtail Documentation](https://docs.wagtail.org/)
