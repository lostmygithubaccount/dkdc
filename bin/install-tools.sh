#!/usr/bin/env bash
# Install dkdc development tools

set -euo pipefail

echo "🔧 Installing dkdc development tools..."
echo ""

cd "$(dirname "$0")/../rs"

# Build all tools
echo "Building dkdc-test..."
cargo install --path dkdc-test

echo "Building dkdc-release..."
cargo install --path dkdc-release

echo ""
echo "✅ Development tools installed!"
echo ""
echo "Available commands:"
echo "  dkdc-test    - Run tests"
echo "  dkdc-release - Release automation"