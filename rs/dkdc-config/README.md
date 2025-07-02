# dkdc-config

Configuration management for dkdc (don't know, don't care).

## Overview

This crate provides centralized configuration management for all dkdc components. It handles:

- Path management for dkdc directories
- Configuration constants
- Platform-specific path handling

## Usage

```rust
use dkdc_config::Config;

// Create config with default paths ($HOME/.dkdc)
let config = Config::new()?;

// Get various paths
let lake_dir = config.lake_dir();           // ~/.dkdc/dkdclake
let metadata = config.metadata_path();      // ~/.dkdc/dkdclake/metadata.db
let data = config.data_path();              // ~/.dkdc/dkdclake/data
let python = config.python_path();          // ~/.dkdc/venv/bin/python

// Ensure directories exist
config.ensure_directories()?;
config.ensure_metadata_db()?;
```

## Directory Structure

```
~/.dkdc/
├── dkdclake/
│   ├── metadata.db     # SQLite metadata database
│   └── data/           # DuckLake encrypted data files
├── venv/               # Python virtual environment
└── config.toml         # User configuration (future)
```

## Constants

The crate exports several important constants:

- Table names: `SECRETS_TABLE_NAME`, `FILES_TABLE_NAME`, `ARCHIVES_TABLE_NAME`
- Extensions: `DUCKLAKE_EXTENSION`, `SQLITE_EXTENSION`
- UI colors: `Colors::PRIMARY`, `Colors::SECONDARY`, etc.
- ASCII banner: `DKDC_BANNER`

## Platform Support

- Cross-platform path handling (Unix/Windows)
- Automatic Python executable path resolution
- Home directory detection via `HOME` or `USERPROFILE`

## Dependencies

Minimal dependencies:
- `anyhow`: Error handling
- `toml`: Configuration file parsing (future)