# Publishing dkdc to crates.io

This guide explains how to publish the dkdc Rust crates to crates.io.

## Prerequisites

1. You must have a crates.io account and API token configured:
   ```bash
   cargo login
   ```

2. Ensure all tests pass:
   ```bash
   ./bin/test.sh
   ```

3. Check that code is properly formatted:
   ```bash
   ./bin/check.sh
   ```

## Publishing Process

Use the release script to automate the publishing process:

```bash
# Check if ready for release
./bin/release.sh check

# Build release artifacts
./bin/release.sh build

# Publish all packages
./bin/release.sh publish

# Or publish only Rust crates
./bin/release.sh publish --rust-only
```

## Manual Publishing

If you need to publish manually, the crates must be published in dependency order:

```bash
cd rs

# 1. Common utilities (no dependencies)
cargo publish -p dkdc-common

# 2. Core data lake functionality
cargo publish -p dkdc-lake

# 3. Crates that depend on lake
cargo publish -p dkdc-files
cargo publish -p dkdc-secrets
cargo publish -p dkdc-archive
cargo publish -p dkdc-config

# 4. Development environment
cargo publish -p dkdc-dev

# 5. Main CLI (depends on most others)
cargo publish -p dkdc-cli

# 6. Standalone tools
cargo publish -p dkdc-links
cargo publish -p dkdc-release
```

Note: `dkdc-py` is the Python extension and is NOT published to crates.io.

## Version Management

All crates use workspace-level version management. To bump the version:

1. Update the version in `/rs/Cargo.toml`:
   ```toml
   [workspace.package]
   version = "0.2.0"  # New version
   ```

2. Commit the change:
   ```bash
   git add rs/Cargo.toml
   git commit -m "chore: bump version to 0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

## Troubleshooting

- **"crate version already exists"**: You need to bump the version number
- **"failed to verify package"**: Usually means a dependency hasn't been published yet
- **"waiting for crates.io to update"**: Wait 1-2 minutes between publishing dependent crates