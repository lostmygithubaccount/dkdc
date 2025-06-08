# dkdc-rs Architecture

A Rust implementation of the dkdc CLI tool for managing bookmarks in your terminal.

## Overview

`dkdc-rs` is a command-line application that allows users to quickly open URLs, applications, and files through configurable aliases and bookmarks. It's designed as a Rust port of the original Go implementation with full feature parity.

## Project Structure

```
packages/dkdc-rs/
├── src/
│   ├── main.rs      # CLI entry point and argument parsing
│   ├── lib.rs       # Library exports
│   ├── config.rs    # Configuration management
│   └── open.rs      # URL/file opening logic
├── Cargo.toml       # Project configuration and dependencies
└── ARCHITECTURE.md  # This file
```

## Components

### `main.rs` - CLI Interface
- Uses `clap` for command-line argument parsing
- Handles the main application flow:
  - `--config/-c`: Opens config file in `$EDITOR`
  - No arguments: Prints current configuration
  - Arguments: Opens specified things/aliases
- Implements async main with `tokio`

### `config.rs` - Configuration Management
- Manages `~/.dkdc/config.toml` file
- Defines `Config` struct with `aliases` and `things` sections
- Creates default configuration if none exists
- Provides functions for:
  - `init_config()`: Initialize config directory and file
  - `load_config()`: Parse TOML config into struct
  - `config_it()`: Open config file in editor
  - `print_config()`: Display formatted config sections

### `open.rs` - Opening Logic
- Resolves aliases to things and things to URIs
- Uses the `open` crate for cross-platform opening
- Implements parallel processing with configurable worker count
- Functions:
  - `alias_or_thing_to_uri()`: Resolve input to final URI
  - `open_it()`: Open a single URI/path
  - `open_things()`: Process multiple items concurrently

## Configuration Format

The configuration file uses TOML format:

```toml
[aliases]
g = "github"
d = "drive"

[things]
github = "https://github.com"
drive = "https://drive.google.com"
```

- **aliases**: Short names that map to thing names
- **things**: Named URLs, file paths, or applications

## Dependencies

- **clap**: Command-line argument parsing with derive macros
- **toml**: TOML configuration file parsing
- **serde**: Serialization/deserialization for config struct
- **open**: Cross-platform URL/file opening
- **dirs**: Home directory detection
- **tokio**: Async runtime for parallel processing
- **anyhow**: Error handling with context
- **num_cpus**: CPU count detection for worker limits

## Key Features

1. **Cross-platform**: Uses `open` crate for macOS, Linux, and Windows support
2. **Async/parallel**: Can open multiple items concurrently with configurable worker limits
3. **Alias resolution**: Two-level lookup (alias → thing → URI)
4. **Error handling**: Graceful error messages for missing items
5. **Editor integration**: Opens config in `$EDITOR` (defaults to `vi`)
6. **Zero-config**: Creates sensible defaults on first run

## Installation

```bash
cargo install --path rs
```

This installs the `dkdc-rs` binary, which can be used as:

```bash
dkdc-rs              # Show configuration
dkdc-rs -c           # Edit configuration
dkdc-rs github       # Open GitHub
dkdc-rs g d          # Open GitHub and Drive (via aliases)
dkdc-rs -m 4 a b c   # Open a, b, c with 4 workers
```

## Future Considerations

- Python bindings (PyO3) planned for integration with top-level Python package
- Additional output formats (JSON, etc.)
- Shell completion scripts
- Config validation and migration tools
