#!/usr/bin/env bash
# Development helper script

set -e

echo "Building dkdc with maturin..."
uv run maturin develop

echo ""
echo "✓ Development build complete!"
echo ""
echo "You can now use:"
echo "  uv run dkdc --help"
echo ""