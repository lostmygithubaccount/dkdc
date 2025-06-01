#!/usr/bin/env bash

# Build static sites in production mode

set -euo pipefail

echo "Building static sites..."

# Build dkdc.dev
echo "Building dkdc.dev..."
docker compose exec -T dkdc-dev bash -c "cd /app/websites/dkdc.dev && zola build --base-url https://dkdc.dev"

# Build dkdc.io  
echo "Building dkdc.io..."
docker compose exec -T dkdc-io bash -c "cd /app/websites/dkdc.io && zola build --base-url https://dkdc.io"

echo "Copying built files to nginx..."

# Create directories if needed
docker compose exec -T nginx mkdir -p /var/www/dkdc.dev /var/www/dkdc.io

# Copy built files from containers to nginx
docker cp dkdc-dkdc-dev-1:/app/websites/dkdc.dev/public/. - | docker cp - dkdc-nginx-1:/var/www/dkdc.dev
docker cp dkdc-dkdc-io-1:/app/websites/dkdc.io/public/. - | docker cp - dkdc-nginx-1:/var/www/dkdc.io

echo "Static sites built and deployed!"