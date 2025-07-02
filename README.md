# dkdc

***don't know, don't care*** - A modular data lake management system with encryption, virtual filesystem, and development tools.

## Features

- 🔐 **Encrypted Storage** - All data encrypted at rest using DuckLake
- 📁 **Virtual Filesystem** - Store and organize files in a virtual filesystem
- 🔑 **Secrets Management** - Secure storage for API keys and passwords
- 📦 **Directory Archiving** - Archive directories with gitignore support
- 🚀 **Development REPL** - Interactive Python/SQL environment for data exploration
- 🦀 **Written in Rust** - Fast, safe, and reliable

## Installation

### Prerequisites

- [uv](https://docs.astral.sh/uv/getting-started/installation) - For Python environment management
- [Rust](https://rustup.rs/) - For building from source (optional)

### Quick Install

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dkdc as a tool (from PyPI)
uv tool install dkdc

# Or install from git
uv tool install git+https://github.com/lostmygithubaccount/dkdc
```

### Development Install

```bash
# Clone the repository
git clone https://github.com/lostmygithubaccount/dkdc.git
cd dkdc

# Create virtual environment
uv venv

# Build the Rust extensions and install in development mode
uv run maturin develop

# Now you can use dkdc
uv run dkdc --help
```

> [!NOTE]
> After making changes to Rust code, run `uv run maturin develop` to rebuild.

## Usage

### Development REPL

Enter an interactive Python environment with DuckDB and ibis pre-configured:

```bash
# Python REPL (default)
dkdc dev

# SQL REPL
dkdc dev --sql
```

### Files Management

Work with files in the virtual filesystem:

```bash
# Add a file
dkdc files add README.md

# List files
dkdc files list

# Open a file
dkdc files open README.md

# Dump all files to local directory
dkdc files dump ./output

# Restore files from directory
dkdc files restore ./backup
```

### Secrets Management

Securely store and retrieve secrets:

```bash
# Set a secret (interactive)
dkdc secrets set API_KEY

# Set a secret directly
dkdc secrets set API_KEY --value "your-secret-value"

# Get a secret
dkdc secrets get API_KEY

# List all secrets
dkdc secrets list

# Export secrets
dkdc secrets export              # Shell format to stdout
dkdc secrets export -f json       # JSON format
dkdc secrets export -f dotenv     # .env format
dkdc secrets export .env          # Write to file
```

### Archive Directories

Archive directories to the data lake:

```bash
# Archive current directory
dkdc archive

# Archive specific directory
dkdc archive /path/to/project

# Archive with custom name
dkdc archive /path/to/project --name backup-2024.zip
```

### Configuration

Edit the configuration file:

```bash
dkdc --config
```

Configuration is stored at `~/.config/dkdc/config.toml`.

## Architecture

dkdc is implemented in Rust for performance and safety, with Python bindings for ease of use. The Python package you install contains a compiled Rust extension that provides all functionality.

### How It Works

1. **Rust Core**: All functionality implemented in modular Rust crates
2. **Python Extension**: `dkdc-py` crate compiles to a Python extension module using PyO3
3. **Python Package**: Thin wrapper that imports the Rust extension
4. **Single Distribution**: One wheel contains everything - no separate Rust installation needed

### Key Components

- **dkdc-config** - Configuration management
- **dkdc-lake** - Core DuckDB/DuckLake functionality
- **dkdc-dev** - Development REPL
- **dkdc-files** - Virtual filesystem
- **dkdc-secrets** - Secrets management
- **dkdc-archive** - Directory archiving
- **dkdc-py** - Python bindings (what makes the Python package work)
- **dkdc-cli** - Standalone Rust CLI (alternative to Python package)

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

## Data Storage

All data is stored encrypted using DuckDB with the DuckLake extension:

- **Location**: `~/.dkdc/dkdclake/`
- **Metadata**: SQLite database at `~/.dkdc/dkdclake/metadata.db`
- **Data**: Encrypted files in `~/.dkdc/dkdclake/data/`

## Development

### Setup Development Environment

```bash
# Clone the repository
gh repo clone lostmygithubaccount/dkdc
cd dkdc

# Set up the development environment
./bin/setup.sh

# Build the Rust extensions (required for first use)
uv run maturin develop

# Run code checks (lint & format)
./bin/check.sh

# Run the development REPL
uv run dkdc dev
```

### Organization

- [`py/`](py): Python package code (thin CLI wrapper around Rust extension)
- [`rs/`](rs): Rust source code (all actual implementation)
  - `dkdc-py/`: Python extension module that bridges Python↔Rust
  - Other crates: Core functionality
- [`bin/`](bin): Repository utilities and scripts
- [`tasks/`](tasks): Development tasks
- [`dotfiles/`](dotfiles): Dotfiles
- [`websites/`](websites): Static websites

### Development Workflow

1. Make changes to Rust code
2. Run `uv run maturin develop` to rebuild
3. Test with `uv run dkdc`

### Building for Release

```bash
# Build wheel for distribution
uv run maturin build --release

# The wheel will be in target/wheels/
ls target/wheels/
```

## Security

- All data is encrypted at rest using DuckLake
- Secrets are stored as encrypted BLOBs
- No secrets are logged or displayed unless explicitly requested
- Virtual environment is isolated in `~/.dkdc/venv/`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Built with:
- [DuckDB](https://duckdb.org/) - In-process analytical database
- [DuckLake](https://github.com/duckdb/duckdb_ducklake) - Encryption extension for DuckDB
- [Rust](https://www.rust-lang.org/) - Systems programming language
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager