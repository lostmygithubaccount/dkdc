#!/usr/bin/env bash

set -euo pipefail

if [ -z "${UV_PUBLISH_TOKEN:-}" ]; then
    echo "Error: UV_PUBLISH_TOKEN environment variable is not set"
    exit 1
fi

rm -rf dist
uv build
uv publish --token "${UV_PUBLISH_TOKEN}"
