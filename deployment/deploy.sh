#!/bin/bash
# Deployment script for aclarknet Django application
# Usage: ./deploy.sh [--initial]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="aclarknet"
DEPLOY_USER="nginx"
DEPLOY_GROUP="nginx"
DEPLOY_DIR="/srv/${APP_NAME}"
REPO_URL="https://github.com/aclark4life/aclarknet.git"
SYSTEMD_DIR="/etc/systemd/system"
NGINX_CONF_DIR="/etc/nginx/conf.d"

# Use production settings
export DJANGO_SETTINGS_MODULE="aclarknet.settings.production"

echo -e "${GREEN}Starting deployment of ${APP_NAME}...${NC}"

# Check if this is an initial deployment
INITIAL_DEPLOY=false
if [[ "$1" == "--initial" ]]; then
    INITIAL_DEPLOY=true
    echo -e "${YELLOW}Running initial deployment setup...${NC}"
fi

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}This script must be run as root (use sudo)${NC}"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    echo -e "${GREEN}Creating necessary directories...${NC}"
    mkdir -p ${DEPLOY_DIR}/{logs,static,media}

    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} ${DEPLOY_DIR}
}

# Clone or update repository
setup_repository() {
    # Define rsync exclude patterns
    local RSYNC_EXCLUDES="--exclude='.git' --exclude='node_modules' --exclude='.venv' --exclude='venv'"

    if [ "$INITIAL_DEPLOY" = true ]; then
        echo -e "${GREEN}Cloning repository...${NC}"
        # Clone to a temporary directory first
        if [ -d "/tmp/aclarknet-deploy" ]; then
            rm -rf /tmp/aclarknet-deploy
        fi
        git clone ${REPO_URL} /tmp/aclarknet-deploy

        # Copy files to deploy directory (excluding .git, node_modules, and venv directories)
        rsync -av $RSYNC_EXCLUDES \
              /tmp/aclarknet-deploy/ ${DEPLOY_DIR}/
        rm -rf /tmp/aclarknet-deploy
    else
        echo -e "${GREEN}Updating repository...${NC}"
        # Clone to temp and rsync
        if [ -d "/tmp/aclarknet-deploy" ]; then
            rm -rf /tmp/aclarknet-deploy
        fi
        git clone ${REPO_URL} /tmp/aclarknet-deploy

        # Sync files (excluding virtual environments, node_modules, and existing runtime data)
        rsync -av $RSYNC_EXCLUDES \
              --exclude='logs' --exclude='static' --exclude='media' --exclude='.env' \
              /tmp/aclarknet-deploy/ ${DEPLOY_DIR}/
        rm -rf /tmp/aclarknet-deploy
    fi
    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} ${DEPLOY_DIR}
}

# Setup Python virtual environment
setup_virtualenv() {
    echo -e "${GREEN}Setting up Python virtual environment...${NC}"

    # Check if Python 3.13 is installed
    if ! command -v python3.13 &> /dev/null; then
        echo -e "${RED}Python 3.13 is not installed!${NC}"
        echo -e "${YELLOW}On Amazon Linux 2023, install it with:${NC}"
        echo -e "  sudo dnf install python3.13 python3.13-pip python3.13-devel"
        exit 1
    fi

    if [ ! -d "${DEPLOY_DIR}/.venv" ]; then
        python3.13 -m venv ${DEPLOY_DIR}/.venv
    fi
    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} ${DEPLOY_DIR}/.venv
}

# Install Python dependencies
install_dependencies() {
    echo -e "${GREEN}Installing Python dependencies...${NC}"
    cd ${DEPLOY_DIR}
    ${DEPLOY_DIR}/.venv/bin/pip install --upgrade pip
    ${DEPLOY_DIR}/.venv/bin/pip install -e .
}

# Setup environment file
setup_env_file() {
    if [ ! -f "${DEPLOY_DIR}/.env" ]; then
        echo -e "${YELLOW}Creating .env file from example...${NC}"
        cp ${DEPLOY_DIR}/deployment/.env.example ${DEPLOY_DIR}/.env
        echo -e "${RED}IMPORTANT: Edit ${DEPLOY_DIR}/.env with your production settings!${NC}"
        echo -e "${RED}Especially: DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS, and database settings${NC}"
        chown ${DEPLOY_USER}:${DEPLOY_GROUP} ${DEPLOY_DIR}/.env
        chmod 600 ${DEPLOY_DIR}/.env
    else
        echo -e "${GREEN}.env file already exists. Skipping...${NC}"
    fi
}

# Build frontend assets
build_frontend() {
    echo -e "${GREEN}Building frontend assets...${NC}"
    cd ${DEPLOY_DIR}

    # Install Node.js dependencies if not already installed
    if [ ! -d "node_modules" ]; then
        npm install
    fi

    # Build production assets
    npm run build
}

# Collect static files
collect_static() {
    echo -e "${GREEN}Collecting static files...${NC}"
    cd ${DEPLOY_DIR}
    ${DEPLOY_DIR}/.venv/bin/python manage.py collectstatic --noinput
}

# Run migrations
run_migrations() {
    echo -e "${GREEN}Running database migrations...${NC}"
    cd ${DEPLOY_DIR}
    ${DEPLOY_DIR}/.venv/bin/python manage.py migrate --noinput
}

# Setup The Lounge IRC client
setup_thelounge() {
    echo -e "${GREEN}Setting up The Lounge IRC client...${NC}"

    # Install Node.js dependencies
    cd ${DEPLOY_DIR}/lounge
    if [ ! -d "node_modules" ]; then
        echo -e "${GREEN}Installing The Lounge dependencies...${NC}"
        npm install
    else
        echo -e "${YELLOW}The Lounge dependencies already installed${NC}"
    fi

    # Ensure .thelounge directory exists
    if [ ! -d "${DEPLOY_DIR}/lounge/.thelounge" ]; then
        echo -e "${RED}Error: .thelounge configuration directory not found${NC}"
        exit 1
    fi

    # Set proper ownership
    chown -R nginx:nginx ${DEPLOY_DIR}/lounge
}

# Setup systemd services
setup_systemd() {
    echo -e "${GREEN}Setting up systemd services...${NC}"
    cp ${DEPLOY_DIR}/deployment/aclarknet.service ${SYSTEMD_DIR}/
    cp ${DEPLOY_DIR}/deployment/thelounge.service ${SYSTEMD_DIR}/
    systemctl daemon-reload
    systemctl enable aclarknet.service
    systemctl enable thelounge.service
}

# Setup nginx configuration
setup_nginx() {
    echo -e "${GREEN}Setting up nginx configuration...${NC}"
    cp ${DEPLOY_DIR}/deployment/nginx-aclarknet.conf ${NGINX_CONF_DIR}/aclarknet.conf

    echo -e "${YELLOW}NOTE: Update SSL certificate paths in ${NGINX_CONF_DIR}/aclarknet.conf${NC}"
    echo -e "${YELLOW}Then run: nginx -t && systemctl reload nginx${NC}"
}

# Restart services
restart_services() {
    echo -e "${GREEN}Restarting services...${NC}"
    systemctl restart aclarknet.service
    systemctl restart thelounge.service

    # Check status
    if systemctl is-active --quiet aclarknet.service; then
        echo -e "${GREEN}aclarknet service is running${NC}"
    else
        echo -e "${RED}aclarknet service failed to start. Check logs with: journalctl -u aclarknet.service -n 50${NC}"
        exit 1
    fi

    if systemctl is-active --quiet thelounge.service; then
        echo -e "${GREEN}thelounge service is running${NC}"
    else
        echo -e "${YELLOW}WARNING: thelounge service failed to start. Check logs with: journalctl -u thelounge.service -n 50${NC}"
    fi
}

# Main deployment flow
main() {
    check_root
    create_directories
    setup_repository
    setup_virtualenv
    install_dependencies
    setup_env_file
    setup_thelounge

    if [ "$INITIAL_DEPLOY" = true ]; then
        setup_systemd
        setup_nginx
    fi

    build_frontend
    collect_static
    run_migrations
    restart_services

    echo -e "${GREEN}Deployment complete!${NC}"
    echo -e "${GREEN}Next steps:${NC}"
    echo -e "  1. Edit ${DEPLOY_DIR}/.env with your production settings"
    echo -e "  2. Obtain SSL certificates for all domains:"
    echo -e "     certbot --nginx -d aclark.net -d www.aclark.net -d m.aclark.net"
    echo -e "  3. Test nginx config: nginx -t"
    echo -e "  4. Reload nginx: systemctl reload nginx"
    echo -e "  5. Check application: https://aclark.net"
    echo -e "  6. Create superuser: ${DEPLOY_DIR}/.venv/bin/python ${DEPLOY_DIR}/manage.py createsuperuser"
    echo -e "  7. Create The Lounge users:"
    echo -e "     cd ${DEPLOY_DIR}/lounge && node_modules/.bin/thelounge add <username>"
    echo -e "  8. Access The Lounge: https://aclark.net/lounge/"
}

main
