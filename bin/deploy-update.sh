#!/usr/bin/env bash

# Deploy updates to dkdc production server
# Usage: ./bin/deploy-update.sh [host]

set -euo pipefail

# Configuration
VPS_HOST="${1:-$VPS_IP}"
DEPLOY_USER="dkdc"
DEPLOY_DIR="/opt/dkdc"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

function warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if we have a host
if [ -z "$VPS_HOST" ]; then
    echo "Error: No host specified. Usage: $0 <host-or-ip>"
    echo "Or set VPS_IP environment variable"
    exit 1
fi

log "🚀 Starting deployment to $VPS_HOST..."

# Check connection
log "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 root@"$VPS_HOST" "echo 'Connection successful'" > /dev/null 2>&1; then
    echo "Error: Cannot connect to $VPS_HOST"
    echo "Make sure you can SSH as root to the server"
    exit 1
fi

# Pull latest changes (handle any local changes gracefully)
log "Pulling latest changes from GitHub..."
ssh root@"$VPS_HOST" "cd $DEPLOY_DIR && \
    git fetch origin main && \
    git reset --hard origin/main"

# Rebuild static sites
log "Building static sites..."
ssh root@"$VPS_HOST" "cd $DEPLOY_DIR && ./bin/build-static.sh"

# Restart app service (Panel app)
log "Restarting application services..."
ssh root@"$VPS_HOST" "cd $DEPLOY_DIR && docker compose restart app1"

# Quick health check
log "Running health check..."
ssh root@"$VPS_HOST" "cd $DEPLOY_DIR && docker compose ps"

# Show URLs
echo
echo -e "${BLUE}=== Deployment Complete! ===${NC}"
echo -e "✅ ${GREEN}https://dkdc.dev${NC}"
echo -e "✅ ${GREEN}https://dkdc.io${NC}"
echo -e "✅ ${GREEN}https://app.dkdc.io${NC}"
echo
echo -e "View logs: ${YELLOW}ssh root@$VPS_HOST 'cd $DEPLOY_DIR && docker compose logs -f'${NC}"

log "✨ Deployment successful!"