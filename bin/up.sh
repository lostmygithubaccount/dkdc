#!/usr/bin/env bash

# Set strict mode
set -euo pipefail

function run_command() {
    local command="$1"
    echo "Running: $command"
    eval "$command"
}

run_command "docker compose up -d $*"
