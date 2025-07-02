#!/usr/bin/env bash
# Setup development environment

set -euo pipefail

echo "🚀 Setting up dkdc development environment..."
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    
    if ! command -v curl &> /dev/null; then
        echo "❌ Error: curl is required to install uv but is not installed"
        exit 1
    fi
    
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo ""
fi

# Create fresh virtual environment
echo "🐍 Creating virtual environment..."
rm -rf .venv
uv venv

# Sync dependencies
echo "📦 Installing dependencies..."
uv sync

# Build the project
echo ""
./bin/build.sh
