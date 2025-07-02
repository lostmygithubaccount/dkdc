# dkdc-files

File management library and CLI for dkdc virtual filesystem.

## Overview

This crate provides:
1. A library with file management functions
2. A standalone CLI binary for file operations

Both the standalone `dkdc-files` CLI and the main `dkdc` CLI use the same library functions, ensuring consistent behavior.

## Installation

```bash
cargo install --path .
```

## Usage

### As a CLI

```bash
# List files
dkdc-files list
dkdc-files list ./documents

# Add a file
dkdc-files add myfile.pdf
dkdc-files add myfile.pdf --path ./documents

# Open a file in editor
dkdc-files open work.md
dkdc-files open report.pdf --path ./documents

# Dump all files to local directory
dkdc-files dump
dkdc-files dump ./backup

# Restore files from directory
dkdc-files restore ./backup
```

### As a Library

```rust
use dkdc_files::{list_files, add_file, open_file, dump_files, restore_files};

// List files
list_files("./files")?;

// Add a file
add_file("document.pdf", Some("./documents"))?;

// Open file in editor
open_file("notes.md", "./files")?;

// Dump files
dump_files("./backup")?;

// Restore files
restore_files("./backup")?;
```

## Architecture

- Library functions in `src/lib.rs` provide the core functionality
- Thin CLI wrapper in `src/main.rs` for standalone usage
- Shared by both `dkdc` and `dkdc-files` binaries

## Dependencies

- `dkdc-config`: Configuration management
- `dkdc-lake`: Core lake functionality
- `clap`: CLI argument parsing
- `anyhow`: Error handling