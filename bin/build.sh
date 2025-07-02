#!/usr/bin/env bash
# Build dkdc for development

set -euo pipefail

echo "🔨 Building dkdc..."
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
fi

# Install maturin if needed
echo "📦 Installing build dependencies..."
uv pip install maturin

# Build the Rust extensions in development mode
echo "🦀 Building Rust extensions..."
uv run maturin develop

echo ""
echo "✅ Build complete!"
echo ""
echo "You can now run: uv run dkdc --help"
echo ""