#!/bin/bash
# Test script to validate deployment configuration
# This script checks that the deployment files are properly configured

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Testing deployment configuration..."
echo ""

# Test 1: Check deployment script syntax
echo "✓ Test 1: Checking deployment script syntax..."
bash -n "${SCRIPT_DIR}/deploy.sh"
echo "  ✓ deploy.sh has valid bash syntax"

# Test 2: Check for correct virtual environment path in deploy.sh
echo ""
echo "✓ Test 2: Checking virtual environment paths in deploy.sh..."
if grep -q "\.venv" "${SCRIPT_DIR}/deploy.sh"; then
    echo "  ✓ deploy.sh uses .venv (correct)"
else
    echo "  ✗ deploy.sh does not use .venv"
    exit 1
fi

if grep -q "/srv/aclarknet/venv" "${SCRIPT_DIR}/deploy.sh"; then
    echo "  ✗ deploy.sh still references old venv path"
    exit 1
else
    echo "  ✓ deploy.sh does not reference old venv path"
fi

# Test 3: Check systemd service file
echo ""
echo "✓ Test 3: Checking systemd service configuration..."
if grep -q "WorkingDirectory=/srv/aclarknet" "${SCRIPT_DIR}/aclarknet.service"; then
    echo "  ✓ Working directory is /srv/aclarknet"
else
    echo "  ✗ Working directory is not set correctly"
    exit 1
fi

if grep -q "PYTHONPATH=/srv/aclarknet" "${SCRIPT_DIR}/aclarknet.service"; then
    echo "  ✓ PYTHONPATH is set to /srv/aclarknet"
else
    echo "  ✗ PYTHONPATH is not set"
    exit 1
fi

if grep -q "/srv/aclarknet/\.venv/bin/gunicorn" "${SCRIPT_DIR}/aclarknet.service"; then
    echo "  ✓ Gunicorn path uses .venv"
else
    echo "  ✗ Gunicorn path does not use .venv"
    exit 1
fi

# Test 4: Check that deploy.sh uses correct project paths
echo ""
echo "✓ Test 4: Checking project deployment paths..."
if grep -q "rsync" "${SCRIPT_DIR}/deploy.sh" && grep -q "\${DEPLOY_DIR}" "${SCRIPT_DIR}/deploy.sh"; then
    echo "  ✓ deploy.sh uses rsync to deploy directly to DEPLOY_DIR"
else
    echo "  ✗ deploy.sh does not use rsync properly"
    exit 1
fi

# Check that /repo references are removed (except REPO_URL which is expected)
REPO_REFS=$(grep "/repo" "${SCRIPT_DIR}/deploy.sh" | grep -v "REPO_URL" | wc -l)
if [ "$REPO_REFS" -eq 0 ]; then
    echo "  ✓ deploy.sh does not use /repo subdirectory"
else
    echo "  ✗ deploy.sh still references /repo subdirectory"
    exit 1
fi

# Test 5: Verify Python can import with PYTHONPATH
echo ""
echo "✓ Test 5: Testing Python imports with PYTHONPATH..."
cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT"
if python3 -c "import home" 2>/dev/null; then
    echo "  ✓ 'home' module can be imported with PYTHONPATH set"
else
    echo "  ✗ 'home' module cannot be imported"
    exit 1
fi

# Test 6: Check environment file example
echo ""
echo "✓ Test 6: Checking environment file example..."
if [ -f "${SCRIPT_DIR}/.env.example" ]; then
    echo "  ✓ .env.example exists"
    
    # Check for important variables
    for var in DJANGO_SECRET_KEY DJANGO_ALLOWED_HOSTS MONGODB_URI; do
        if grep -q "$var" "${SCRIPT_DIR}/.env.example"; then
            echo "  ✓ .env.example contains $var"
        else
            echo "  ✗ .env.example missing $var"
            exit 1
        fi
    done
else
    echo "  ✗ .env.example does not exist"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ All deployment configuration tests passed!"
echo "=========================================="
echo ""
echo "Summary of deployment structure:"
echo "  • Virtual environment: /srv/aclarknet/.venv"
echo "  • Django project: /srv/aclarknet"
echo "  • PYTHONPATH: /srv/aclarknet"
echo "  • Working directory: /srv/aclarknet"
echo ""
echo "The configuration should resolve the 'home' import issue by:"
echo "  1. Setting PYTHONPATH=/srv/aclarknet in systemd service"
echo "  2. Setting WorkingDirectory=/srv/aclarknet in systemd service"
echo "  3. Using /srv/aclarknet/.venv for the virtual environment"
