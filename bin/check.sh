#!/usr/bin/env bash

set -euo pipefail

ruff check --fix
ruff check --select I --fix
ruff format
