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
    mkdir -p /run/gunicorn
    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} ${DEPLOY_DIR}
    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} /run/gunicorn
}

# Clone or update repository
setup_repository() {
    if [ "$INITIAL_DEPLOY" = true ]; then
        echo -e "${GREEN}Cloning repository...${NC}"
        if [ -d "${DEPLOY_DIR}/repo" ]; then
            echo -e "${YELLOW}Repository directory already exists. Removing...${NC}"
            rm -rf ${DEPLOY_DIR}/repo
        fi
        git clone ${REPO_URL} ${DEPLOY_DIR}/repo
    else
        echo -e "${GREEN}Updating repository...${NC}"
        cd ${DEPLOY_DIR}/repo
        git fetch origin
        git reset --hard origin/main  # or your production branch
    fi
    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} ${DEPLOY_DIR}/repo
}

# Setup Python virtual environment
setup_virtualenv() {
    echo -e "${GREEN}Setting up Python virtual environment...${NC}"
    if [ ! -d "${DEPLOY_DIR}/venv" ]; then
        python3.13 -m venv ${DEPLOY_DIR}/venv
    fi
    chown -R ${DEPLOY_USER}:${DEPLOY_GROUP} ${DEPLOY_DIR}/venv
}

# Install Python dependencies
install_dependencies() {
    echo -e "${GREEN}Installing Python dependencies...${NC}"
    cd ${DEPLOY_DIR}/repo
    ${DEPLOY_DIR}/venv/bin/pip install --upgrade pip
    ${DEPLOY_DIR}/venv/bin/pip install -e .
}

# Setup environment file
setup_env_file() {
    if [ ! -f "${DEPLOY_DIR}/.env" ]; then
        echo -e "${YELLOW}Creating .env file from example...${NC}"
        cp ${DEPLOY_DIR}/repo/deployment/.env.example ${DEPLOY_DIR}/.env
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
    cd ${DEPLOY_DIR}/repo
    
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
    cd ${DEPLOY_DIR}/repo
    ${DEPLOY_DIR}/venv/bin/python manage.py collectstatic --noinput
}

# Run migrations
run_migrations() {
    echo -e "${GREEN}Running database migrations...${NC}"
    cd ${DEPLOY_DIR}/repo
    ${DEPLOY_DIR}/venv/bin/python manage.py migrate --noinput
}

# Setup systemd services
setup_systemd() {
    echo -e "${GREEN}Setting up systemd services...${NC}"
    cp ${DEPLOY_DIR}/repo/deployment/aclarknet.service ${SYSTEMD_DIR}/
    cp ${DEPLOY_DIR}/repo/deployment/aclarknet.socket ${SYSTEMD_DIR}/
    systemctl daemon-reload
    systemctl enable aclarknet.socket
    systemctl enable aclarknet.service
}

# Setup nginx configuration
setup_nginx() {
    echo -e "${GREEN}Setting up nginx configuration...${NC}"
    cp ${DEPLOY_DIR}/repo/deployment/nginx-aclarknet.conf ${NGINX_CONF_DIR}/aclarknet.conf
    
    echo -e "${YELLOW}NOTE: Update SSL certificate paths in ${NGINX_CONF_DIR}/aclarknet.conf${NC}"
    echo -e "${YELLOW}Then run: nginx -t && systemctl reload nginx${NC}"
}

# Restart services
restart_services() {
    echo -e "${GREEN}Restarting services...${NC}"
    systemctl restart aclarknet.socket
    systemctl restart aclarknet.service
    
    # Check status
    if systemctl is-active --quiet aclarknet.service; then
        echo -e "${GREEN}aclarknet service is running${NC}"
    else
        echo -e "${RED}aclarknet service failed to start. Check logs with: journalctl -u aclarknet.service -n 50${NC}"
        exit 1
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
    echo -e "  2. Update SSL certificate paths in ${NGINX_CONF_DIR}/aclarknet.conf"
    echo -e "  3. Test nginx config: nginx -t"
    echo -e "  4. Reload nginx: systemctl reload nginx"
    echo -e "  5. Check application: https://m.aclark.net"
    echo -e "  6. Create superuser: ${DEPLOY_DIR}/venv/bin/python ${DEPLOY_DIR}/repo/manage.py createsuperuser"
}

main
