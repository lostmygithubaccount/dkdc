#!/usr/bin/env bash

# Update script to run on the server
# This is called by deploy-update.sh or can be run manually

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Ensure we're in the right directory
cd /opt/dkdc

log "Pulling latest changes..."
git fetch origin main
git reset --hard origin/main

log "Building static sites..."
./bin/build-static.sh

log "Restarting dynamic services..."
docker compose restart app1

log "Checking service health..."
docker compose ps

log "✅ Update complete!"