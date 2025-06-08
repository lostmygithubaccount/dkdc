#!/bin/bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Generate timestamped filename (UTC)
TIMESTAMP=$(date -u +%Y%m%d_%H%M%S)
ENCRYPTED_FILE="metadata_backup_${TIMESTAMP}.sql.enc"
BUCKET="gs://dkdc-dl"
LAKE_DATA_DIR="$HOME/lake/data"

# Postgres configuration (must match utils.py)
POSTGRES_CONTAINER_NAME="dkdc-dl-metadata"
POSTGRES_USER="dkdc"
POSTGRES_DB="dkdc"

# Check hostname
echo -e "${YELLOW}🖥️ Checking hostname...${NC}"

if [[ "$(hostname)" != dkdcsot* ]]; then
    echo -e "${RED}❌ This script must be run from hostname starting with 'dkdcsot'${NC}"
    echo -e "${RED}Current hostname: $(hostname)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Hostname confirmed: dkdcsot${NC}"

# Check gcloud authentication
echo -e "${YELLOW}🔐 Checking gcloud authentication...${NC}"

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${RED}❌ Not logged into gcloud${NC}"
    echo -e "${YELLOW}Please run: gcloud auth login${NC}"
    exit 1
fi

echo -e "${GREEN}✅ gcloud authentication confirmed${NC}"

# Ensure Postgres container is running
echo -e "${YELLOW}🐘 Ensuring Postgres container is ready...${NC}"
if ! uv run dkdc dev --exit; then
    echo -e "${RED}❌ Failed to start Postgres container${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Creating and encrypting metadata backup...${NC}"
echo "OpenSSL will prompt for the encryption passphrase twice:"
echo -e "${YELLOW}Note: If passphrases don't match, OpenSSL will show 'Verify failure' and you'll need to retry${NC}"

# Create backup and encrypt directly via pipe - never touches disk in plaintext
if docker exec "$POSTGRES_CONTAINER_NAME" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | \
   openssl enc -aes-256-cbc -salt -pbkdf2 -out "$ENCRYPTED_FILE"; then
    echo -e "${GREEN}✅ Backup created and encrypted: ${ENCRYPTED_FILE}${NC}"
else
    echo -e "${RED}❌ Backup or encryption failed${NC}"
    echo -e "${RED}This usually means:${NC}"
    echo -e "${RED}  - Passphrases didn't match (OpenSSL shows 'Verify failure')${NC}"
    echo -e "${RED}  - Database connection issue${NC}"
    echo -e "${RED}  - Postgres container not running${NC}"
    rm -f "$ENCRYPTED_FILE"  # Remove any partial encrypted file
    exit 1
fi

# Upload to cloud storage
echo -e "${YELLOW}☁️ Uploading to cloud storage...${NC}"

# Copy encrypted metadata backup (no sync, just add)
if gsutil cp "$ENCRYPTED_FILE" "${BUCKET}/metadata/"; then
    echo -e "${GREEN}✅ Metadata backup uploaded: ${BUCKET}/metadata/${ENCRYPTED_FILE}${NC}"
else
    echo -e "${RED}❌ Metadata upload failed${NC}"
    exit 1
fi

# Rsync data directory (exact sync with deletions)
if [[ -d "$LAKE_DATA_DIR" ]]; then
    echo -e "${YELLOW}📂 Syncing data directory...${NC}"
    if gsutil -m rsync -r -d "$LAKE_DATA_DIR/" "${BUCKET}/data/"; then
        echo -e "${GREEN}✅ Data directory synced: ${BUCKET}/data/${NC}"
    else
        echo -e "${RED}❌ Data sync failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ Data directory not found: ${LAKE_DATA_DIR}${NC}"
fi

echo -e "${GREEN}🎉 Backup and sync complete!${NC}"
