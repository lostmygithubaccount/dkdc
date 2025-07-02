# dkdc-lake

Core DuckDB/DuckLake functionality for dkdc (don't know, don't care).

## Overview

This crate provides the core data lake functionality using DuckDB with the DuckLake extension for encrypted storage. It implements:

- DuckDB connection management with DuckLake extension
- File storage and retrieval
- Secret management with encryption
- Archive storage
- Virtual filesystem abstraction

## Architecture

The lake uses a two-database architecture:
- **metadata.db**: SQLite database storing metadata
- **data/**: DuckLake encrypted data files

All data is stored using a unified file-based schema:
```sql
CREATE TABLE {table_name} (
    filepath VARCHAR,      -- Virtual path (e.g., "./files", "./secrets")
    filename VARCHAR,      -- File or secret name
    filedata BLOB,        -- Actual content
    filesize BIGINT,      -- Size in bytes
    fileupdated TIMESTAMP -- Last update time
)
```

## Usage

```rust
use dkdc_lake::Lake;

// Create a new lake instance
let lake = Lake::new()?;

// Store a file
lake.add_file("./documents", "report.pdf", &file_data)?;

// Retrieve a file
if let Some(file) = lake.get_file("./documents", "report.pdf")? {
    println!("File size: {} bytes", file.filesize);
}

// Store a secret
lake.set_secret("api_key", b"secret_value")?;

// List files in a directory
let files = lake.list_files("./documents")?;
```

## Features

- **Encrypted Storage**: All data is encrypted at rest using DuckLake
- **Version History**: Stores all versions of files/secrets
- **Virtual Filesystem**: Organize data using virtual paths
- **SQL Access**: Direct SQL access for advanced queries

## SQL Commands

Get the SQL commands to set up the lake manually:
```rust
let sql = lake.get_sql_commands();
```

This returns:
```sql
INSTALL ducklake;
INSTALL sqlite;
ATTACH '/path/to/metadata.db' AS metadata;
ATTACH 'ducklake:sqlite:/path/to/metadata.db' AS data (DATA_PATH '/path/to/data', ENCRYPTED);
USE data;
```

## Dependencies

- `duckdb`: DuckDB database with bundled support
- `dkdc-config`: Configuration management
- `chrono`: Timestamp handling
- `anyhow`: Error handling