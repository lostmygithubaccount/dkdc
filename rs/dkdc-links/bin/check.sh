#!/usr/bin/env bash
set -euo pipefail

echo "Running cargo fmt..."
cargo fmt

echo "Running cargo clippy..."
cargo clippy -- -D warnings

echo "Running cargo check..."
cargo check

echo "All checks passed!"