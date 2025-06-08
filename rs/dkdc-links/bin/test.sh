#!/usr/bin/env bash
set -euo pipefail

echo "Running tests..."
cargo test --all-features

echo "Building release binary..."
cargo build --release

echo "All tests passed!"