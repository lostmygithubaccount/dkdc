# dkdc Rust Implementation

The Rust implementation of dkdc (don't know, don't care) provides a high-performance, modular architecture for the data lake functionality.

## Architecture

The codebase is organized into several focused crates:

### Core Libraries

- **[dkdc-common](./dkdc-common/)**: Shared utilities
  - Version management
  - Common types and functions

- **[dkdc-config](./dkdc-config/)**: Configuration management
  - Centralized path handling
  - Platform-specific configuration
  - Shared constants and settings

- **[dkdc-lake](./dkdc-lake/)**: Core DuckDB/DuckLake functionality
  - DuckDB connection management
  - DuckLake encrypted storage
  - File, secret, and archive management
  - Virtual filesystem abstraction

- **[dkdc-dev](./dkdc-dev/)**: Development REPL functionality
  - SQL mode via DuckDB CLI
  - Python mode via IPython
  - Database setup and initialization

- **[dkdc-files](./dkdc-files/)**: File management operations
  - Virtual filesystem CRUD operations
  - Temporary file handling
  - Directory dumping/restoring

- **[dkdc-secrets](./dkdc-secrets/)**: Secrets management
  - Encrypted key-value storage
  - Multiple export formats
  - Clipboard integration

- **[dkdc-archive](./dkdc-archive/)**: Directory archiving
  - ZIP archive creation
  - Gitignore support
  - Storage in data lake

### CLI Applications

- **[dkdc-cli](./dkdc-cli/)**: Main command-line interface
  - Integrates all library functionality
  - Provides unified CLI experience
  - Built with clap for robust argument parsing

- **[dkdc-dev](./dkdc-dev/)**: Standalone development REPL
  - Can be installed and used independently
  - Same functionality as `dkdc dev` subcommand
  
- **[dkdc-files](./dkdc-files/)**: Standalone file management
  - Can be installed and used independently  
  - Same functionality as `dkdc files` subcommands

### Python Integration

- **[dkdc-py](./dkdc-py/)**: Python extension module
  - PyO3-based bindings for all Rust functionality
  - Compiles to `_dkdc` module imported by Python
  - Enables the Python package to use Rust code directly
  - No subprocess calls - native Python/Rust interop

## Building

Build all crates:
```bash
cd rs
cargo build --release
```

The main binary will be at `rs/target/release/dkdc`.

## Development

Run tests:
```bash
cargo test
```

Check code:
```bash
cargo check
cargo clippy
```

## Design Principles

1. **Minimal Dependencies**: Each crate only includes essential dependencies
2. **Modular Architecture**: Clear separation of concerns between crates
3. **Cross-Platform**: Works on Linux, macOS, and Windows
4. **Performance**: Native Rust performance with embedded DuckDB
5. **Safety**: Leverages Rust's memory safety guarantees

## Modular CLI Architecture

The project supports two usage patterns:

1. **Monolithic**: Install `dkdc` for all functionality in one binary
2. **Modular**: Install individual tools (`dkdc-dev`, `dkdc-files`, etc.) for specific functionality

Key benefits:
- Shared library code ensures consistent behavior
- Smaller binaries when only specific functionality is needed
- Independent versioning and deployment
- No subprocess spawning between components

## Integration with Python

The Rust implementation is fully integrated with Python through the `dkdc-py` crate:

- **Direct Integration**: Python imports the compiled `_dkdc` extension module
- **No Subprocesses**: All calls are native Python→Rust function calls
- **Type Safety**: PyO3 handles conversions between Python and Rust types
- **Single Distribution**: Python wheel includes both Python code and compiled extension
- **Development**: Use `uv run maturin develop` to rebuild the extension during development

This architecture means Python users get:
1. Native Rust performance
2. Standard Python package experience
3. No need to install Rust toolchain
4. Identical functionality to standalone Rust CLI

