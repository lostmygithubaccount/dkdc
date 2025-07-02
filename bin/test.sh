#!/usr/bin/env bash
# Run all tests using the Rust test runner

set -euo pipefail

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Build the test tool if needed
if ! command -v dkdc-test &> /dev/null; then
    echo "🔨 Building test tool..."
    cd rs
    cargo build --release -p dkdc-test
    cd ..
    TEST_TOOL="./rs/target/release/dkdc-test"
else
    TEST_TOOL="dkdc-test"
fi

# Pass through to the test tool
exec $TEST_TOOL "$@"