# Quick Deployment Guide

This is a quick reference for deploying aclarknet to aclark.net (including www.aclark.net and m.aclark.net).

## Using `just` Commands (Recommended)

If you have `just` installed, you can use these convenient commands:

```bash
# Initial deployment
just deploy-initial  # or: just di

# Update deployment
just deploy  # or: just dp

# Check service status
just deploy-status  # or: just ds

# View logs
just deploy-logs  # or: just dl

# Restart service
just deploy-restart  # or: just dr
```

## Manual Deployment

### Initial Deployment (First Time)

```bash
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
cd /srv/aclarknet/repo
sudo -u nginx /srv/aclarknet/venv/bin/python manage.py createsuperuser

# 9. Check status
sudo systemctl status aclarknet.service
```

## Subsequent Deployments

```bash
# SSH to server
ssh user@aclark.net

# Run deployment script
sudo aclarknet-deploy
```

## Quick Checks

```bash
# Check service status
sudo systemctl status aclarknet.service

# View logs
sudo journalctl -u aclarknet.service -n 50
sudo tail -f /srv/aclarknet/logs/gunicorn-error.log

# Restart service
sudo systemctl restart aclarknet.service
```

## File Locations

- Application: `/srv/aclarknet/repo`
- Virtual Environment: `/srv/aclarknet/venv`
- Environment Config: `/srv/aclarknet/.env`
- Logs: `/srv/aclarknet/logs/`
- Static Files: `/srv/aclarknet/static/`
- Media Files: `/srv/aclarknet/media/`
- Systemd Service: `/etc/systemd/system/aclarknet.service`
- nginx Config: `/etc/nginx/conf.d/aclarknet.conf`

For detailed documentation, see [Deployment Guide](deployment_guide)
