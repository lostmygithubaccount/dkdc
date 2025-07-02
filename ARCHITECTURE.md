# dkdc Architecture

## Overview

dkdc (don't know, don't care) is a modular data lake management system built in Rust with Python bindings. It provides encrypted storage, virtual filesystem capabilities, secrets management, and archiving functionality using DuckDB with the DuckLake extension.

## Design Principles

1. **Modular Architecture**: Each major feature is its own crate that can be used independently
2. **Unix Philosophy**: Simple, composable tools with clean interfaces
3. **Security First**: All data is encrypted at rest using DuckLake
4. **Developer Experience**: Easy to use CLI with sensible defaults

## Project Structure

```
dkdc/
├── rs/                     # Rust implementation
│   ├── dkdc-common/       # Shared utilities and version info
│   ├── dkdc-config/       # Configuration management
│   ├── dkdc-lake/         # Core DuckDB/DuckLake functionality
│   ├── dkdc-dev/          # Development REPL support
│   ├── dkdc-files/        # Virtual filesystem operations
│   ├── dkdc-secrets/      # Secrets management
│   ├── dkdc-archive/      # Directory archiving
│   ├── dkdc-cli/          # Standalone CLI application
│   └── dkdc-py/           # PyO3 Python bindings
├── py/                    # Python package
│   └── dkdc/
│       ├── __init__.py    # Package initialization
│       └── cli/
│           └── main.py    # CLI entry point
└── tasks/                 # Development tasks and documentation
```

## Core Components

### dkdc-common

Shared utilities and types used across all dkdc crates.

**Key Features:**
- Version management (single source of truth)
- Common types and helper functions
- Shared across all crates to ensure consistency

### dkdc-config

Central configuration management for all dkdc components.

**Key Features:**
- Path management (~/.dkdc directory structure)
- Configuration file handling (~/.config/dkdc/config.toml)
- Shared constants and banners

**Important Paths:**
- `~/.dkdc/` - Main dkdc directory
- `~/.dkdc/dkdclake/` - DuckLake data directory
- `~/.dkdc/dkdclake/metadata.db` - SQLite metadata database
- `~/.dkdc/dkdclake/data/` - Encrypted data files
- `~/.dkdc/venv/` - Python virtual environment for dev mode

### dkdc-lake

Core data lake functionality using DuckDB with DuckLake extension.

**Key Features:**
- DuckDB connection management
- DuckLake extension for encryption
- Table creation and management
- File, secret, and archive storage abstractions

**Storage Model:**
All data is stored in DuckDB tables with the following schema:
```sql
CREATE TABLE [files|secrets|archives] (
    filepath VARCHAR,      -- Virtual directory path
    filename VARCHAR,      -- File/secret/archive name
    filedata BLOB,        -- Binary data
    filesize BIGINT,      -- Size in bytes
    fileupdated TIMESTAMP -- Last update time
)
```

### dkdc-dev

Development REPL functionality for interactive data exploration.

**Key Features:**
- Python mode with IPython REPL
- SQL mode with DuckDB CLI
- Automatic environment setup using `uv`
- Pre-configured with ibis and DuckDB connections

**Environment Management:**
- Uses `uv` for fast, reliable Python environment setup
- Automatically syncs packages on each run
- Requirements: ipython, duckdb, ibis-framework[duckdb,sqlite]
- Launches IPython directly with `-c` flag (no temporary files)

### dkdc-files

Virtual filesystem implementation for storing files in the data lake.

**Key Features:**
- Add files to virtual paths
- List files in directories
- Open files with system default applications
- Dump all files to local directory
- Restore files from local directory
- Uses `tempfile` crate for secure temporary file handling

**Library Interface:**
```rust
pub fn list_files(path: &str) -> Result<()>
pub fn add_file(file: &str, path: Option<&str>) -> Result<()>
pub fn open_file(name: &str, path: &str) -> Result<()>
pub fn dump_files(output: &str) -> Result<()>
pub fn restore_files(directory: &str) -> Result<()>
```

### dkdc-secrets

Secure secrets management with encryption.

**Key Features:**
- Set/get/delete secrets
- List all secrets
- Export in multiple formats (shell, dotenv, JSON)
- Clipboard support
- Force overwrite protection
- Read from stdin

**Security:**
- Secrets are stored as encrypted BLOBs in DuckLake
- No secrets are ever logged or displayed unless explicitly requested

### dkdc-archive

Directory archiving with gitignore support.

**Key Features:**
- Archive directories as ZIP files
- Respects .gitignore patterns
- Stores archives in the data lake
- Automatic naming based on directory

### dkdc-cli

Standalone Rust CLI application that provides a unified interface to all functionality.

**Architecture:**
- Uses library crates (not subprocess calls)
- Supports both monolithic and modular installation
- Unix-style output (simple, pipeable)
- Comprehensive help and error messages

### dkdc-py

PyO3-based Python extension module that bridges the Python and Rust implementations.

**Purpose:**
This crate is the critical link between Python and Rust, allowing Python users to access all dkdc functionality through native Python bindings rather than subprocess calls. It compiles to a module named `_dkdc` that the Python package imports directly.

**Key Features:**
- Direct Python bindings to all Rust functionality (no subprocess overhead)
- Handles type conversions between Python and Rust seamlessly
- Provides native Python functions for:
  - `run_cli()` - Main CLI entry point
  - `list_files()`, `add_file()` - File operations
  - `get_secret()`, `set_secret()`, `list_secrets()`, `delete_secret()` - Secrets management
  - `launch_dev()` - Development REPL
  - `get_connection_string()` - Database connection info

**Build Process:**
- Built with maturin for seamless Python packaging
- Compiles to `_dkdc.so` (Linux/Mac) or `_dkdc.pyd` (Windows)
- Packaged as part of the Python wheel distribution
- The Python CLI (`py/dkdc/cli/main.py`) is just a thin wrapper around these bindings

**Why This Architecture:**
- **Performance**: Native Rust speed with no subprocess overhead
- **Simplicity**: Python users get a normal Python package experience
- **Type Safety**: PyO3 ensures proper type conversions
- **Distribution**: Single wheel contains both Python code and compiled extension

## Data Flow

### Rust CLI Flow
1. **User Input** → CLI parses commands and arguments
2. **Configuration** → Config module provides paths and settings
3. **Lake Connection** → Lake module establishes DuckDB connection with DuckLake
4. **Operations** → Specific modules handle operations (files, secrets, etc.)
5. **Storage** → Data is encrypted and stored in DuckDB tables
6. **Output** → Results are returned in Unix-friendly format

### Python Package Flow
1. **User Input** → `dkdc` command (Python script)
2. **Python CLI** → `py/dkdc/cli/main.py` imports `_dkdc` extension
3. **Rust Extension** → `dkdc-py` provides native Python bindings
4. **Rust Libraries** → Same core libraries as Rust CLI
5. **Storage** → Same encrypted DuckDB/DuckLake backend
6. **Output** → Results returned as Python objects or printed

The key insight is that both flows use the exact same Rust implementation - Python users just access it through the `_dkdc` extension module instead of a standalone binary.

## Security Model

### Encryption
- All data is encrypted at rest using DuckLake extension
- Encryption keys are managed by DuckLake
- SQLite metadata database stores encrypted references

### Secrets Management
- Secrets are stored as encrypted BLOBs
- No plaintext logging
- Clipboard integration for secure copying

### Planned: Backup System
- Triple-layer encryption with AES-256-CBC
- Three separate passphrases for defense in depth
- Cloud storage integration for offsite backups

## Installation Options

### Monolithic Installation
```bash
cargo install --path rs/dkdc-cli
```
Installs the main `dkdc` command with all subcommands.

### Modular Installation
```bash
cargo install --path rs/dkdc-files
cargo install --path rs/dkdc-secrets
cargo install --path rs/dkdc-archive
cargo install --path rs/dkdc-dev
```
Installs individual commands: `dkdc-files`, `dkdc-secrets`, etc.

### Python Package (Recommended)
```bash
# From PyPI
uv tool install dkdc

# Development mode
uv run maturin develop
```
Installs the Python package with compiled Rust extension. This is the recommended way to use dkdc as it provides:
- Native Python bindings (no subprocess overhead)
- Seamless integration with Python tooling
- Single wheel distribution with everything included
- Identical functionality to the Rust CLI

## Development Workflow

1. **Rust Development**
   - Each crate can be developed independently
   - Use `cargo test` in individual crates
   - Use `cargo build --workspace` to build everything

2. **Python Integration**
   - Python package provides a thin CLI wrapper
   - All functionality implemented in Rust via `dkdc-py` extension
   - Use `uv run maturin develop` to rebuild after Rust changes
   - No business logic in Python - it's just the entry point

3. **Testing**
   - Unit tests in each Rust crate
   - Integration tests in dkdc-cli
   - Manual testing with example commands

## Dependencies

### Core Dependencies
- **duckdb**: Embedded analytical database
- **clap**: Command-line argument parsing
- **anyhow**: Error handling

### Feature-Specific
- **zip**: Archive creation
- **walkdir**: Directory traversal
- **rpassword**: Secure password input
- **clipboard**: System clipboard integration
- **serde_json**: JSON serialization

### Development Environment
- **uv**: Fast Python package management
- **ipython**: Interactive Python shell
- **ibis-framework**: Python dataframe library