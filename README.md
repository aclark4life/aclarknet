[![CI/CD Pipeline](https://github.com/aclark4life/aclarknet/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/aclark4life/aclarknet/actions/workflows/ci-cd.yml)

(Written by [us.amazon.nova-micro-v1:0](https://github.com/aclark4life/aclarknet/blob/0d39a6525465a7ea4083177b4e536f98de19fd88/justfile#L5))

This is a project that includes various configuration files and directories for different tools and environments.

## Table of Contents

- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration Files](#configuration-files)
- [Directory Structure](#directory-structure)
- [Django Management Commands](#django-management-commands)
- [Production Deployment](#production-deployment)
- [License](#license)
- [Deployment Commands Summary](#deployment-commands-summary)

## Project Structure

The project directory contains several important files and subdirectories:

### Configuration Files

#### Babel
- **.babelrc**: Configuration file for Babel.
- **.browserslistrc**: Configuration file for specifying browser targets.

#### ESLint
- **.eslintrc**: Configuration file for ESLint.

#### Git
- **.gitignore**: Specifies intentionally untracked files to ignore.
- **.git**: Git repository directory.

#### Node.js
- **.nvmrc**: Node version manager configuration file.
- `package-lock.json`: Lock file for npm dependencies.
- `package.json`: Package manager configuration file.

#### Python
- **.venv**: Virtual environment directory.
- **pyproject.toml**: Configuration file for PEP 518/517.

#### Stylelint
- **.stylelintrc.json**: Configuration file for Stylelint.

### Development and Build Tools

- **justfile**: Scripting file for task automation.
- **postcss.config.js**: Configuration file for PostCSS.

### Directory Structure

- **db**: Directory for database files.
- **frontend**: Directory containing frontend code.
- **manage.py**: Django management script.
- **aclarknet**: Directory or module named `aclarknet`.
- **aclarknet.egg-info**: Information about the `aclarknet` distribution package.

### Other Files

- **README.md**: Documentation file you are currently reading.
- **.git**: Git repository metadata.

## Getting Started

To get started with this project, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2. **Install dependencies**:
    For Node.js:
    ```bash
    npm install
    ```
    For Python:
    ```bash
    python -m venv .venv
    source.venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3. **Run the project**:
    Instructions for running the project will vary based on the type of project (e.g., web application, backend service).

## Django Management Commands

This project includes custom Django management commands for common tasks.

### Repository Management (`repo`)

The `repo` command helps manage git repository operations.

**Sync with upstream:**
```bash
# Using dm wrapper (short syntax)
dm repo sync

# Or using manage.py directly
python manage.py repo sync

# Sync with custom upstream remote
dm repo sync --upstream origin

# Sync specific branch
dm repo sync --branch develop
```

The `sync` action fetches from the upstream remote and rebases your current branch on top of it. This is useful for keeping your fork up to date with the upstream repository.

**Note:** Make sure you have an `upstream` remote configured, or specify a different remote with `--upstream`.

## GitHub Social Authentication

This project supports GitHub OAuth authentication using django-allauth. To enable GitHub login:

### 1. Create a GitHub OAuth App

1. Go to GitHub Settings → Developer settings → [OAuth Apps](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the application details:
   - **Application name**: Your app name (e.g., "AClark.net")
   - **Homepage URL**: `http://localhost:8000` (for development) or your production URL
   - **Authorization callback URL**: `http://localhost:8000/accounts/github/login/callback/` (for development)
4. Click "Register application"
5. Note your **Client ID** and generate a **Client Secret**

### 2. Configure the Django Admin

1. Start your development server:
    ```bash
    python manage.py runserver
    ```

2. Log in to the Django admin at `http://localhost:8000/admin/`

3. Navigate to **Sites** and ensure you have a site configured:
   - Domain name: `localhost:8000` (for development)
   - Display name: Your site name

4. Navigate to **Social applications** under the "Social Accounts" section

5. Click "Add social application" and configure:
   - **Provider**: GitHub
   - **Name**: GitHub (or any name you prefer)
   - **Client id**: Paste your GitHub OAuth App Client ID
   - **Secret key**: Paste your GitHub OAuth App Client Secret
   - **Sites**: Select your site from "Available sites" and move it to "Chosen sites"

6. Save the configuration

### 3. Test the Login

1. Navigate to `http://localhost:8000/accounts/login/`
2. You should see a "Sign in with GitHub" button
3. Click it to test the GitHub OAuth flow

### 4. GitHub Username Whitelist (Optional)

You can restrict GitHub login to specific usernames by setting the `GITHUB_USERNAME_WHITELIST` environment variable:

```bash
# In your .env file or environment
GITHUB_USERNAME_WHITELIST=username1,username2,username3
```

**How it works:**
- If `GITHUB_USERNAME_WHITELIST` is not set or empty, all GitHub users can login (default behavior)
- If set, only GitHub usernames in the comma-separated list can login
- Usernames are case-sensitive and should match the GitHub username exactly
- Whitespace around usernames is automatically trimmed

**Example:**
```bash
# Only allow these three GitHub users to login
GITHUB_USERNAME_WHITELIST=alice,bob,charlie
```

When a non-whitelisted user tries to login, they will see an error message and be redirected back to the login page.

### 5. Signup Restrictions

**Regular account signups are DISABLED** to prevent unauthorized access.

**What this means:**
- ❌ Users cannot self-register at `/accounts/signup/`
- ✅ Whitelisted GitHub users can auto-create accounts on first login
- ✅ Existing users can login normally
- ✅ Admins can create new users via Django admin

**How it works:**

**For Regular Signups:**
- The signup page at `/accounts/signup/` is disabled
- Users cannot create accounts with username/password

**For GitHub OAuth:**
- If `GITHUB_USERNAME_WHITELIST` is configured:
  - ✅ Whitelisted users can auto-create accounts on first GitHub login
  - ❌ Non-whitelisted users are blocked
- If `GITHUB_USERNAME_WHITELIST` is NOT configured:
  - ❌ All GitHub signups are blocked (secure by default)

**For Other Social Providers (Google, Facebook, etc.):**
- ❌ All signups are disabled

**Example Flow - Whitelisted GitHub User:**
```bash
# Set whitelist
GITHUB_USERNAME_WHITELIST=alice,bob,charlie

# When 'alice' clicks "Sign in with GitHub" for the first time:
# 1. GitHub authenticates the user
# 2. System checks: Is 'alice' in whitelist? YES ✓
# 3. System checks: Does 'alice' have an account? NO
# 4. System auto-creates account for 'alice' ✓
# 5. 'alice' is logged in ✓
```

**To allow a new user to access the system:**

**Option 1: Add to GitHub Whitelist (Recommended)**
1. Add their GitHub username to `GITHUB_USERNAME_WHITELIST`
2. User clicks "Sign in with GitHub"
3. Account is auto-created on first login

**Option 2: Manual Account Creation**
1. Admin creates a user account via Django admin at `/admin/`
2. User can login with their credentials or link their GitHub account

This security feature ensures that only authorized users can access the system.

### Production Configuration

For production, update:
- GitHub OAuth App callback URL to: `https://yourdomain.com/accounts/github/login/callback/`
- Site domain in Django admin to your production domain
- Ensure `ALLOWED_HOSTS` in settings includes your production domain
- Optionally set `GITHUB_USERNAME_WHITELIST` to restrict access

## Production Deployment

This project includes comprehensive deployment configuration for deploying to a production server with nginx and systemd.

### Quick Start

For deploying to m.aclark.net (or any Amazon Linux 2023 server):

**Using `just` (Recommended):**

```bash
# On your server
git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy
cd /tmp/aclarknet-deploy

# Install just if needed
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

# Initial deployment
just deploy-initial  # or: just di

# Subsequent deployments
just deploy  # or: just dp
```

**Alternative (using deployment script directly):**

```bash
# On your server
git clone https://github.com/aclark4life/aclarknet.git /tmp/aclarknet-deploy
cd /tmp/aclarknet-deploy
sudo cp deployment/deploy.sh /usr/local/bin/aclarknet-deploy
sudo chmod +x /usr/local/bin/aclarknet-deploy
sudo aclarknet-deploy --initial
```

### Documentation

- **[Quick Start Guide](docs/deployment_quickstart.md)** - Quick reference for deployment
- **[Comprehensive Deployment Guide](docs/deployment_guide.md)** - Detailed deployment instructions, troubleshooting, and maintenance
- **[Full Documentation](docs/)** - Complete Sphinx documentation

### What's Included

The deployment configuration includes:

- **Gunicorn systemd service** - Production WSGI server configuration
- **nginx configuration** - Reverse proxy with HTTPS support
- **Deployment script** - Automated deployment and updates
- **Environment configuration** - Production settings template
- **Production Django settings** - Security hardened configuration
- **`just` commands** - Convenient deployment commands (`just deploy`, `just deploy-status`, etc.)

All deployment files are located in the `deployment/` directory.

### Common Deployment Commands (via `just`)

```bash
just deploy-initial  # Initial deployment (alias: just di)
just deploy          # Update deployment (alias: just dp)
just deploy-status   # Check service status (alias: just ds)
just deploy-logs     # View logs (alias: just dl)
just deploy-restart  # Restart service (alias: just dr)
```

## Deployment Commands Summary

Below are the commands used for setting up and configuring the Nginx web server, obtaining an SSL certificate using Certbot, and managing the Nginx configuration.

### Install Nginx
```bash
sudo dnf install nginx
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Install Certbot for Nginx
```bash
sudo dnf install python3-certbot-nginx -y
```

### Obtain SSL Certificate using Certbot
```bash
sudo certbot --nginx -d www.aclark.net -d aclark.net
```

### Edit Nginx Configuration
```bash
sudo vi /etc/nginx/nginx.conf
```

### Restart Nginx
```bash
sudo systemctl restart nginx
```

These commands will help you set up Nginx, obtain an SSL certificate, and configure your web server for secure connections.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
