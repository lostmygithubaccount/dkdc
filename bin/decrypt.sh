#!/bin/bash

# decrypt.sh: Decrypt files encrypted with backup.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if file argument provided
if [[ $# -ne 1 ]]; then
    echo -e "${RED}❌ Usage: $0 <encrypted_file.enc>${NC}"
    exit 1
fi

ENCRYPTED_FILE="$1"

# Check if file exists
if [[ ! -f "$ENCRYPTED_FILE" ]]; then
    echo -e "${RED}❌ File not found: $ENCRYPTED_FILE${NC}"
    exit 1
fi

# Check if file ends in .enc
if [[ ! "$ENCRYPTED_FILE" =~ \.enc$ ]]; then
    echo -e "${RED}❌ File must end in .enc${NC}"
    exit 1
fi

# Generate output filename (remove .enc extension)
OUTPUT_FILE="${ENCRYPTED_FILE%.enc}"

# Check if output file already exists
if [[ -f "$OUTPUT_FILE" ]]; then
    echo -e "${YELLOW}⚠️ Output file already exists: $OUTPUT_FILE${NC}"
    echo -n "Overwrite? (y/N): "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Cancelled${NC}"
        exit 0
    fi
fi

echo -e "${YELLOW}🔓 Decrypting: $ENCRYPTED_FILE${NC}"
echo "OpenSSL will prompt for the decryption passphrase:"

# Decrypt the file
if openssl enc -aes-256-cbc -salt -pbkdf2 -d -in "$ENCRYPTED_FILE" -out "$OUTPUT_FILE"; then
    echo -e "${GREEN}✅ File decrypted: $OUTPUT_FILE${NC}"
else
    echo -e "${RED}❌ Decryption failed${NC}"
    echo -e "${RED}This usually means:${NC}"
    echo -e "${RED}  - Incorrect passphrase${NC}"
    echo -e "${RED}  - Corrupted encrypted file${NC}"
    echo -e "${RED}  - File was not encrypted with the expected method${NC}"
    # Remove any partial output file
    rm -f "$OUTPUT_FILE"
    exit 1
fi
