#!/usr/bin/env bash

set -euo pipefail

rm -rf target
cargo build --release
cargo publish
