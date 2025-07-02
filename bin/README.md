# Development Scripts

This directory contains helper scripts for dkdc development.

## Scripts

### `setup.sh`
Sets up the complete development environment:
- Installs uv if not present
- Creates virtual environment
- Installs dependencies
- Builds the Rust extensions

```bash
./bin/setup.sh
```

### `build.sh`
Builds the project for development:
- Installs maturin
- Builds Rust extensions in development mode
- Installs in editable mode

```bash
./bin/build.sh
```

### `release.sh`
Release automation tool for dkdc. Uses the Rust-based `dkdc-release` tool internally.

```bash
# Check if ready for release
./bin/release.sh check

# Build release artifacts
./bin/release.sh build

# Publish to PyPI and crates.io
./bin/release.sh publish

# Publish only Python package
./bin/release.sh publish --python-only

# Publish only Rust crates
./bin/release.sh publish --rust-only

# Dry run (see what would be published)
./bin/release.sh publish --dry-run
```

### `check.sh`
Runs code quality checks for all languages:
- **Python**: ruff (linting & formatting)
- **Rust**: cargo fmt & clippy
- **Go**: go fmt, go vet, golangci-lint (if available)

```bash
./bin/check.sh
```

### `test.sh`
Test runner for dkdc. Uses the Rust-based `dkdc-test` tool internally.

```bash
# Run all tests
./bin/test.sh

# Run only specific test suite
./bin/test.sh rust    # Only Rust tests
./bin/test.sh python  # Only Python tests
./bin/test.sh go      # Only Go tests
./bin/test.sh e2e     # Only end-to-end tests

# Verbose output
./bin/test.sh --verbose
```

### `dev.sh`
Quick development build helper for Python extension.

```bash
./bin/dev.sh
```

### `install-tools.sh`
Installs development tools (dkdc-test, dkdc-release) globally.

```bash
./bin/install-tools.sh
```

## Development Workflow

1. Initial setup: `./bin/setup.sh`
2. (Optional) Install dev tools: `./bin/install-tools.sh`
3. After Rust changes: `./bin/build.sh`
4. Before committing: `./bin/check.sh`
5. Run tests: `./bin/test.sh`
6. For release: `./bin/release.sh`