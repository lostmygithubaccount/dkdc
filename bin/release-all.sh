#!/usr/bin/env bash
# Release everything - Python to PyPI and Rust to crates.io

set -euo pipefail

echo "🚀 Releasing dkdc to PyPI and crates.io"
echo ""

cd "$(dirname "$0")/.."

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
        UV_PUBLISH_TOKEN=$PYPI_TOKEN uv publish "$wheel" || echo "Already published or error"
    fi
done

echo ""
echo "✅ Python package done!"
echo ""

# Publish Rust crates
echo "📦 Publishing Rust crates to crates.io..."
echo ""

cd rs

# Function to publish a crate
publish_crate() {
    local crate=$1
    echo "Publishing $crate..."
    cargo publish -p "$crate" --allow-dirty 2>&1 | grep -E "(Uploading|already uploaded|error)" || true
    sleep 2
}

# Publish in dependency order
publish_crate "dkdc-common"
publish_crate "dkdc-config"
publish_crate "dkdc-lake"
publish_crate "dkdc-files"
publish_crate "dkdc-secrets"
publish_crate "dkdc-archive"
publish_crate "dkdc-dev"
publish_crate "dkdc-cli"
publish_crate "dkdc-links"

echo ""
echo "✅ All done! Published to:"
echo "  - PyPI: https://pypi.org/project/dkdc/"
echo "  - crates.io: https://crates.io/crates/dkdc-cli"