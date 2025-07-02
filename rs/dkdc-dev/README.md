# dkdc-dev

Development REPL functionality for dkdc (don't know, don't care).

## Overview

This crate provides the `dkdc dev` command functionality, launching either:
- **SQL mode**: DuckDB CLI with DuckLake pre-configured
- **Python mode**: IPython shell with DuckDB/DuckLake connection (requires PyO3)

## Features

### SQL Mode
- Launches DuckDB CLI with DuckLake automatically attached
- Pre-configures all necessary extensions (ducklake, sqlite)
- Sets up encrypted data lake connection
- Provides immediate SQL access to your data

### Python Mode (Future)
- Launches IPython with pre-configured namespace
- Provides `ibis` connection to DuckLake
- Includes utility modules for files and secrets
- Will require PyO3 integration for embedded Python

## Usage

```rust
use dkdc_dev::{Dev, DevMode};

// Create dev environment
let dev = Dev::new()?;

// Check if DuckDB CLI is available
if !dev.check_duckdb()? {
    println!("Please install DuckDB CLI");
}

// Launch SQL mode
dev.launch(DevMode::Sql)?;

// Launch Python mode (not yet implemented)
dev.launch(DevMode::Python)?;
```

## SQL Commands

The SQL mode automatically runs:
```sql
INSTALL ducklake;
INSTALL sqlite;
ATTACH '/path/to/metadata.db' AS metadata;
ATTACH 'ducklake:sqlite:/path/to/metadata.db' AS data (DATA_PATH '/path/to/data', ENCRYPTED);
USE data;
```

## Dependencies

- `dkdc-config`: Configuration management
- `dkdc-lake`: Core lake functionality
- `anyhow`: Error handling

## Future Work

Python mode:
- Uses `uv` for Python environment management
- Automatically creates virtual environment at `~/.dkdc/venv`
- Installs IPython, DuckDB, and ibis-framework
- Launches IPython with pre-configured DuckLake connection

## Standalone Usage

This crate can be used as a standalone binary:

```bash
# Install
cargo install --path .

# Launch Python REPL
dkdc-dev

# Launch SQL REPL
dkdc-dev --sql
```

## Library Usage

The same functionality is available as a library:

```rust
use dkdc_dev::{Dev, DevMode};

let dev = Dev::new()?;
dev.launch(DevMode::Python)?;
```

Both `dkdc` and `dkdc-dev` use the same underlying library.