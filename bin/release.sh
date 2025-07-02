#!/usr/bin/env bash
# Complete release script for dkdc

set -euo pipefail

echo "🚀 dkdc Release Script"
echo ""

cd "$(dirname "$0")/.."

# Check for required environment variables
if [ -z "${PYPI_TOKEN:-}" ]; then
    echo "❌ Error: PYPI_TOKEN environment variable not set"
    exit 1
fi

# Build Python package
echo "🐍 Building Python package..."
uv run maturin build --release

# Copy wheels to standard location
mkdir -p target/wheels
cp rs/dkdc-py/target/wheels/*.whl target/wheels/ 2>/dev/null || true

# Publish to PyPI
echo ""
echo "📤 Publishing to PyPI..."
for wheel in target/wheels/*.whl; do
    if [ -f "$wheel" ]; then
        echo "Publishing $(basename "$wheel")..."
        UV_PUBLISH_TOKEN=$PYPI_TOKEN uv publish "$wheel" 2>&1 | grep -E "(Uploading|already exists)" || true
    fi
done

echo ""
echo "✅ Python package published to: https://pypi.org/project/dkdc/"
echo ""

# Publish Rust crates
echo "📦 Publishing Rust crates to crates.io..."
echo ""

cd rs

# Function to publish a crate with error handling
publish_crate() {
    local crate=$1
    echo -n "Publishing $crate... "
    
    if cargo publish -p "$crate" --allow-dirty 2>&1 | grep -q "already exists"; then
        echo "already published ✓"
    elif cargo publish -p "$crate" --allow-dirty 2>&1 | grep -q "Uploading"; then
        echo "published ✓"
        sleep 3  # Rate limit protection
    elif cargo publish -p "$crate" --allow-dirty 2>&1 | grep -q "Too Many Requests"; then
        echo "rate limited ⚠️"
        echo "  Try again later or continue with: cargo publish -p $crate"
        return 1
    else
        echo "error ✗"
        cargo publish -p "$crate" --allow-dirty
    fi
}

# Publish in dependency order
CRATES=(
    "dkdc-common"
    "dkdc-config"
    "dkdc-lake"
    "dkdc-files"
    "dkdc-secrets"
    "dkdc-archive"
    "dkdc-dev"
    "dkdc-cli"
    "dkdc-links"
)

for crate in "${CRATES[@]}"; do
    publish_crate "$crate" || break
done

echo ""
echo "🎉 Release complete!"
echo ""
echo "Published packages:"
echo "  - PyPI: https://pypi.org/project/dkdc/"
echo "  - crates.io: https://crates.io/crates/dkdc-cli"
echo ""
echo "Installation:"
echo "  - Python: uv tool install dkdc"
echo "  - Rust: cargo install dkdc-cli"