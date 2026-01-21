# Deployment Guide for aclarknet

This guide provides instructions for deploying the aclarknet Django/Wagtail application to a production server running Amazon Linux 2023 with nginx.

## Server Requirements

- Amazon Linux 2023
- Python 3.11 or higher
- MongoDB (local or remote instance)
- nginx (already installed and configured with HTTPS)
- Git
- Node.js (for building frontend assets)
- systemd (for service management)

## Prerequisites

1. SSH access to the server (m.aclark.net)
2. sudo/root access
3. MongoDB instance available
4. SSL certificates configured in nginx
5. DNS configured to point m.aclark.net to your server

## Initial Deployment

### 1. Prepare the Server

SSH into your server:
```bash
ssh user@m.aclark.net
```

Install required system packages:
```bash
sudo dnf update -y
sudo dnf install -y python3 python3-pip git mongodb-org nodejs npm
```

Ensure nginx is installed and running:
```bash
sudo systemctl status nginx
```

### 2. Clone the Repository and Run Deployment

```bash
# Clone the repository to a temporary location
git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy
cd /tmp/aclarknet-deploy

# Copy deployment script to a convenient location
sudo cp deployment/deploy.sh /usr/local/bin/aclarknet-deploy
sudo chmod +x /usr/local/bin/aclarknet-deploy

# Run initial deployment
sudo aclarknet-deploy --initial
```

### 3. Configure Environment Variables

Edit the environment file with your production settings:
```bash
sudo nano /srv/aclarknet/.env
```

**Important settings to configure:**

```bash
# Generate a secure secret key (you can use: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DJANGO_SECRET_KEY=your-actual-secret-key-here

# Set allowed hosts
DJANGO_ALLOWED_HOSTS=m.aclark.net,www.m.aclark.net

# Set CSRF trusted origins
DJANGO_CSRF_TRUSTED_ORIGINS=https://m.aclark.net,https://www.m.aclark.net

# MongoDB configuration (adjust if using remote MongoDB)
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=aclarknet

# Email settings (if using email)
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 4. Configure nginx

Edit the nginx configuration to add your SSL certificate paths:
```bash
sudo nano /etc/nginx/conf.d/aclarknet.conf
```

Update these lines with your actual certificate paths:
```nginx
ssl_certificate /path/to/your/fullchain.pem;
ssl_certificate_key /path/to/your/privkey.pem;
```

Test nginx configuration and reload:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Create Django Superuser

```bash
cd /srv/aclarknet/repo
sudo -u nginx /srv/aclarknet/venv/bin/python manage.py createsuperuser
```

### 6. Verify Deployment

1. Check service status:
```bash
sudo systemctl status aclarknet.service
sudo systemctl status aclarknet.socket
```

2. Check logs if there are issues:
```bash
sudo journalctl -u aclarknet.service -n 50
sudo tail -f /srv/aclarknet/logs/gunicorn-error.log
sudo tail -f /srv/aclarknet/logs/django.log
```

3. Visit your site:
- Main site: https://m.aclark.net
- Admin: https://m.aclark.net/admin/
- Wagtail Admin: https://m.aclark.net/wagtail/

## Subsequent Deployments

For updating the application after the initial deployment:

```bash
sudo aclarknet-deploy
```

This will:
1. Pull the latest code from the repository
2. Install any new dependencies
3. Build frontend assets
4. Collect static files
5. Run database migrations
6. Restart the application

## Manual Deployment Steps

If you prefer to deploy manually or need to troubleshoot:

### Update Code
```bash
cd /srv/aclarknet/repo
sudo -u nginx git pull origin main
```

### Install Dependencies
```bash
cd /srv/aclarknet/repo
sudo -u nginx /srv/aclarknet/venv/bin/pip install -e .
```

### Build Frontend
```bash
cd /srv/aclarknet/repo
sudo -u nginx npm install
sudo -u nginx npm run build
```

### Collect Static Files
```bash
cd /srv/aclarknet/repo
sudo -u nginx /srv/aclarknet/venv/bin/python manage.py collectstatic --noinput
```

### Run Migrations
```bash
cd /srv/aclarknet/repo
sudo -u nginx /srv/aclarknet/venv/bin/python manage.py migrate
```

### Restart Services
```bash
sudo systemctl restart aclarknet.service
```

## Troubleshooting

### Service Won't Start

Check the service logs:
```bash
sudo journalctl -u aclarknet.service -n 100
```

Check gunicorn logs:
```bash
sudo tail -n 100 /srv/aclarknet/logs/gunicorn-error.log
```

### Static Files Not Loading

1. Verify static files are collected:
```bash
ls -la /srv/aclarknet/static/
```

2. Check nginx configuration:
```bash
sudo nginx -t
```

3. Check file permissions:
```bash
sudo chown -R nginx:nginx /srv/aclarknet/static/
```

### Database Connection Issues

1. Check MongoDB is running:
```bash
sudo systemctl status mongod
```

2. Verify MongoDB connection string in `/srv/aclarknet/.env`

3. Test connection:
```bash
mongosh $MONGODB_URI
```

### 502 Bad Gateway

This usually means gunicorn isn't running or the socket permissions are wrong:

1. Check gunicorn service:
```bash
sudo systemctl status aclarknet.service
```

2. Check socket file:
```bash
ls -la /run/gunicorn/aclarknet.sock
```

3. Restart services:
```bash
sudo systemctl restart aclarknet.socket
sudo systemctl restart aclarknet.service
```

## Monitoring

### Check Service Status
```bash
sudo systemctl status aclarknet.service
```

### View Live Logs
```bash
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
```

## Security Considerations

1. **Keep SECRET_KEY secret**: Never commit it to version control
2. **Use strong passwords**: For database and Django admin
3. **Regular updates**: Keep system packages and Python dependencies updated
4. **Firewall**: Ensure only necessary ports are open (80, 443, 22)
5. **HTTPS only**: The configuration forces HTTPS redirects
6. **File permissions**: Ensure .env file is only readable by nginx user
7. **Regular backups**: Backup your MongoDB database regularly

## Backup and Restore

### Backup MongoDB
```bash
mongodump --uri="mongodb://localhost:27017/aclarknet" --out=/backup/mongodb/$(date +%Y%m%d)
```

### Restore MongoDB
```bash
mongorestore --uri="mongodb://localhost:27017/aclarknet" /backup/mongodb/20240101/aclarknet/
```

### Backup Media Files
```bash
tar -czf /backup/media-$(date +%Y%m%d).tar.gz /srv/aclarknet/media/
```

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Wagtail Deployment Guide](https://docs.wagtail.org/en/stable/advanced_topics/deploying.html)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [nginx Documentation](https://nginx.org/en/docs/)
