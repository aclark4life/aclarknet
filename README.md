[![CI/CD Pipeline](https://github.com/aclark4life/aclarknet/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/aclark4life/aclarknet/actions/workflows/ci-cd.yml)

(Written by [us.amazon.nova-micro-v1:0](https://github.com/aclark4life/aclarknet/blob/0d39a6525465a7ea4083177b4e536f98de19fd88/justfile#L5))

This is a project that includes various configuration files and directories for different tools and environments.

## Table of Contents

- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration Files](#configuration-files)
- [Directory Structure](#directory-structure)
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
