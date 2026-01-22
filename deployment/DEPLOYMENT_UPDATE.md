# Deployment Update Summary

## Problem Statement
The deployment needed to be reconfigured to:
1. Use virtual environment in `/srv/aclarknet/.venv` (instead of `/srv/aclarknet/venv`)
2. Place Django project files directly in `/srv/aclarknet` (instead of `/srv/aclarknet/repo`)
3. Fix the "home" import error when running with gunicorn

## Root Cause of Import Issue

The "home" import error was caused by Python not being able to locate the Django apps when gunicorn started. This happened because:
- The PYTHONPATH wasn't explicitly set
- The working directory structure wasn't optimal for module imports

## Solution Implemented

### 1. systemd Service Configuration (`deployment/aclarknet.service`)
- Changed virtual environment path: `/srv/aclarknet/venv` → `/srv/aclarknet/.venv`
- Added: `Environment="PYTHONPATH=/srv/aclarknet"` to ensure Python can import all Django apps
- Maintained: `WorkingDirectory=/srv/aclarknet`

### 2. Deployment Script (`deployment/deploy.sh`)
- Changed deployment structure:
  - OLD: Clone to `/srv/aclarknet/repo`, create venv in `/srv/aclarknet/venv`
  - NEW: Clone to temp dir, rsync to `/srv/aclarknet`, create venv in `/srv/aclarknet/.venv`
- Improved rsync patterns to avoid duplication
- Initial deploy excludes: `.git`, `node_modules`, `.venv`, `venv`
- Update deploy additionally excludes: `logs`, `static`, `media`, `.env`

### 3. Documentation (`deployment/README.md`)
- Complete deployment guide with step-by-step instructions
- Troubleshooting section for common issues
- Security best practices
- Architecture overview

### 4. Testing (`deployment/test_deployment_config.sh`)
- Validates deployment script syntax
- Checks virtual environment paths
- Verifies systemd service configuration
- Tests Python imports with PYTHONPATH
- Confirms environment file example exists

## Directory Structure

```
/srv/aclarknet/
├── .venv/                   # Python virtual environment (NEW location)
├── .env                     # Environment variables
├── manage.py                # Django management script (at root level)
├── aclarknet/              # Main Django project
│   ├── settings/
│   ├── wsgi.py
│   └── ...
├── home/                   # Home app (directly importable now)
├── db/                     # Database app
├── cms/                    # CMS app
├── search/                 # Search app
├── siteuser/              # Site user app
├── frontend/              # Frontend assets
├── deployment/            # Deployment configs
├── logs/                  # Application logs
├── static/                # Collected static files
└── media/                 # User uploads
```

## How to Deploy

### Initial Deployment
```bash
# On the server, as root
git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy
sudo cp /tmp/aclarknet-deploy/deployment/deploy.sh /tmp/
sudo chmod +x /tmp/deploy.sh
sudo /tmp/deploy.sh --initial
```

### Updates
```bash
# On the server, as root
sudo /tmp/deploy.sh
```

## Testing the Configuration

```bash
# Test deployment configuration
cd /home/runner/work/aclarknet/aclarknet
./deployment/test_deployment_config.sh

# Test Python imports
cd /srv/aclarknet
sudo -u nginx /srv/aclarknet/.venv/bin/python -c "import home; print('Success')"
```

## Verification

After deployment, verify that:
1. ✅ Virtual environment is at `/srv/aclarknet/.venv`
2. ✅ Django project files are at `/srv/aclarknet` (not in a `repo` subdirectory)
3. ✅ PYTHONPATH is set in systemd service
4. ✅ Working directory is `/srv/aclarknet`
5. ✅ The "home" app can be imported successfully

## Changes from Previous Setup

| Aspect | Old | New |
|--------|-----|-----|
| Virtual env | `/srv/aclarknet/venv` | `/srv/aclarknet/.venv` |
| Project location | `/srv/aclarknet/repo` | `/srv/aclarknet` |
| PYTHONPATH | Not set | `/srv/aclarknet` |
| Deployment method | Git clone in place | Rsync from temp |

## Files Modified

1. `deployment/aclarknet.service` - Updated venv path, added PYTHONPATH
2. `deployment/deploy.sh` - Updated deployment structure and paths

## Files Added

1. `deployment/README.md` - Comprehensive deployment guide
2. `deployment/test_deployment_config.sh` - Configuration validation script
3. `deployment/DEPLOYMENT_UPDATE.md` - This file

## Troubleshooting

### If "home" still cannot be imported:

1. Check systemd service has PYTHONPATH set:
   ```bash
   sudo systemctl cat aclarknet.service | grep PYTHONPATH
   ```

2. Verify working directory:
   ```bash
   sudo systemctl cat aclarknet.service | grep WorkingDirectory
   ```

3. Test import manually:
   ```bash
   cd /srv/aclarknet
   sudo -u nginx /srv/aclarknet/.venv/bin/python -c "import sys; print(sys.path); import home"
   ```

4. Check service logs:
   ```bash
   sudo journalctl -u aclarknet.service -n 50
   ```

### If deployment fails:

1. Run the test script:
   ```bash
   ./deployment/test_deployment_config.sh
   ```

2. Check deployment script syntax:
   ```bash
   bash -n deployment/deploy.sh
   ```

3. Review deployment logs during the deploy process

## Security Notes

- The `.env` file is properly excluded from rsync during updates
- Virtual environment directories are excluded from deployment
- Log files, static files, and media files are preserved during updates
- All files are owned by the `nginx` user with appropriate permissions

## Next Steps

After applying these changes on the production server:

1. Back up the current deployment
2. Run the updated deploy script
3. Verify the service starts correctly
4. Test that all Django apps can be imported
5. Check application logs for any issues
6. Test the web application to ensure it's working properly
