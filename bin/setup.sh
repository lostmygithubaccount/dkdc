#!/usr/bin/env bash

# Set strict mode
set -euo pipefail

function run_command() {
    local command="$1"
    echo "Running: $command"
    eval "$command"
}

if ! command -v uv &> /dev/null; then
    echo "uv not found, installing..."
    
    if ! command -v curl &> /dev/null; then
        echo "Error: curl is required to install uv but is not installed"
        exit 1
    fi
    
    run_command "curl -LsSf https://astral.sh/uv/install.sh | sh"
fi

run_command "rm -rf .venv"
run_command "uv sync"
