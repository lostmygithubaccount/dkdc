#!/usr/bin/env bash
# Quick release script - just build and publish

set -euo pipefail

echo "🚀 Quick release for dkdc"
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Build Python wheel
echo "🐍 Building Python wheel..."
uv run maturin build --release

echo ""
echo "📦 Wheels built:"
ls -la target/wheels/

echo ""
echo "📤 Publishing to PyPI..."
for wheel in target/wheels/*.whl; do
    echo "Publishing $wheel..."
    UV_PUBLISH_TOKEN=$PYPI_TOKEN uv publish "$wheel"
done

echo ""
echo "✅ Python package published!"
echo ""
echo "📦 To publish Rust crates to crates.io, run:"
echo ""
echo "cd rs"
echo "cargo publish -p dkdc-common"
echo "cargo publish -p dkdc-lake" 
echo "cargo publish -p dkdc-files"
echo "cargo publish -p dkdc-secrets"
echo "cargo publish -p dkdc-archive"
echo "cargo publish -p dkdc-config"
echo "cargo publish -p dkdc-dev"
echo "cargo publish -p dkdc-cli"
echo "cargo publish -p dkdc-links"