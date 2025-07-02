#!/usr/bin/env bash
# Run code quality checks

set -euo pipefail

echo "🔍 Running code quality checks..."
echo ""

# Track if any checks fail
FAILED=0

# Python checks
if [ -d "py" ]; then
    echo "🐍 Checking Python code..."
    if command -v ruff &> /dev/null; then
        uv run ruff check --fix py/ || FAILED=1
        uv run ruff check --select I --fix py/ || FAILED=1
        uv run ruff format py/ || FAILED=1
    else
        echo "⚠️  ruff not found, installing..."
        uv pip install ruff
        uv run ruff check --fix py/ || FAILED=1
        uv run ruff check --select I --fix py/ || FAILED=1
        uv run ruff format py/ || FAILED=1
    fi
fi

# Rust checks
if [ -d "rs" ]; then
    echo ""
    echo "🦀 Checking Rust code..."
    cd rs
    
    # Format
    if command -v cargo &> /dev/null; then
        cargo fmt || FAILED=1
        
        # Clippy
        if cargo clippy --version &> /dev/null 2>&1; then
            cargo clippy --all-targets --all-features -- -D warnings || FAILED=1
        else
            echo "⚠️  clippy not found, skipping linting"
        fi
    else
        echo "❌ cargo not found, skipping Rust checks"
        FAILED=1
    fi
    cd ..
fi

# Go checks
if [ -d "go" ] && [ -n "$(find go -name '*.go' 2>/dev/null)" ]; then
    echo ""
    echo "🐹 Checking Go code..."
    
    if command -v go &> /dev/null; then
        # Format
        go fmt ./go/... || FAILED=1
        
        # Vet
        go vet ./go/... || FAILED=1
        
        # golangci-lint if available
        if command -v golangci-lint &> /dev/null; then
            golangci-lint run ./go/... || FAILED=1
        else
            echo "⚠️  golangci-lint not found, skipping advanced linting"
            echo "   Install with: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest"
        fi
    else
        echo "❌ go not found, skipping Go checks"
        FAILED=1
    fi
fi

echo ""
if [ $FAILED -eq 0 ]; then
    echo "✅ All checks passed!"
else
    echo "❌ Some checks failed!"
    exit 1
fi
echo ""
