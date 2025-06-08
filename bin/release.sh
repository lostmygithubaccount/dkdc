#!/usr/bin/env bash

set -euo pipefail

rm -rf dist
uv build
uv publish
