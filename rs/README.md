# dkdc Rust Implementation

The Rust implementation of dkdc (don't know, don't care) provides a high-performance, modular architecture for the data lake functionality.

## Architecture

The codebase is organized into several focused crates:

### Core Libraries

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
  - Python mode via embedded interpreter (future)
  - Database setup and initialization

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

The Rust CLI is designed to be used as a backend for the Python wrapper:
- Python CLI will call the Rust binary for most operations
- Shared configuration ensures compatibility
- Future: Direct Python bindings via PyO3

## Future Work

- [ ] PyO3 integration for embedded Python interpreter
- [ ] Complete implementation of all CLI commands
- [ ] Progress indicators and improved UI
- [ ] Direct Python bindings as alternative to CLI wrapper
- [ ] Performance benchmarks vs Python implementation