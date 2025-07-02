# dkdc-cli

Command-line interface for dkdc (don't know, don't care).

## Overview

This crate provides the main CLI binary for dkdc, integrating all the functionality from the library crates:
- `dkdc-config`: Configuration management
- `dkdc-lake`: Core DuckDB/DuckLake functionality
- `dkdc-dev`: Development REPL functionality

## Installation

Build from source:
```bash
cargo install --path .
```

This will install the `dkdc` binary to your cargo bin directory.

## Commands

### Development REPL
```bash
# Launch IPython REPL (not yet implemented)
dkdc dev

# Launch DuckDB SQL REPL
dkdc dev --sql

# Just setup the database without launching REPL
dkdc dev --exit
```

### Files Management
```bash
# List files in virtual filesystem
dkdc files list
dkdc files list ./documents

# Add a file
dkdc files add myfile.pdf --path ./documents

# Open a file
dkdc files open report.pdf --path ./documents

# Dump all files to local directory
dkdc files dump ./output

# Restore files from directory
dkdc files restore ./backup
```

### Secrets Management
```bash
# Set a secret
dkdc secrets set API_KEY --value "secret-value"

# Get a secret
dkdc secrets get API_KEY
dkdc secrets get API_KEY --clipboard

# List all secrets
dkdc secrets list

# Delete a secret
dkdc secrets delete API_KEY

# Export as .env file
dkdc secrets export
dkdc secrets export ./prod.env
```

### Archive Management
```bash
# Archive a directory
dkdc archive ./myproject
dkdc archive ./myproject --name "project-backup"
```

## Architecture

The CLI is built using:
- `clap`: Command-line argument parsing with derive macros
- `anyhow`: Error handling

Each major command delegates to the appropriate library crate for implementation.

## Future Work

- Full implementation of all commands
- PyO3 integration for Python REPL mode
- Progress indicators and better UI
- Config file editing support