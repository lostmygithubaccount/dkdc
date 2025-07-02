I've created `dkdc`, a developer CLI for myself. It's also the monorepo here, which has different languages and sub-tools. Code is organized (for the purposes of this task) in:

- `py/`: Python code
- `rs/`: Rust code

We want to migrate the bulk of our code to Rust, using Python as a thing wrapper so that people can pip/uv install the tool if they prefer. We mainly need to migrate functionality for `dkdc dev`, a REPL for connecting to DuckLake in DuckDB in Python or SQL, and various functionality for the dkdc lake built on DuckDB + DuckLake. Core functionality should remain the same, but migrated to Rust.

We'll call it `rs/dkdc-lake`. This is a Rust library that will be used by the CLI tool. We should then have a `rs/dkdc-cli` that **implements the full CLI in Rust**. The `py/dkdc` CLI then becomes a very thin wrapper around the Rust CLI library (allowing you to install from both and get the same functionality!).

Then you probably want a `rs/dkdc-dev`. Again `rs/dkdc-cli` picks this up as a subcommand, and the Python CLI can also use it as a thin wrapper.

The Rust CLI, however, will need to embed and use a Python interpreter. It should do this with `uv`, and smartly manage this. Use the `uv` docs as needed, but basically we should follow the existing pattern of using `$HOME/.dkdc/` for data like a Python virtual environemnt. We should ensure it's being used through PyO3 stuff like:

```rust
let use pyo3::prelude::*;

// Point to specific venv interpreter
let interpreter_path = // get the $HOME/.dkdc/venv/bin/python path
```

This will mainly be needed for `dkdc dev`, which enters an IPython shell.

## Instructions

Migrate this in place -- start by building out the Rust libraries out. Get the Rust CLI working well, then migrate the Python CLI to use the Rust library. Keep the existing Python library code around for reference and so that I can check both against each other.

Review the current code and work as a principal software engineer. Run commands via `uv` and `cargo` to test things as you go along.

## Progress

### Completed ✅

1. **Analyzed Python codebase** - Understood the architecture and functionality
2. **Created modular Rust libraries**:
   - `rs/dkdc-config` - Shared configuration management
   - `rs/dkdc-lake` - Core DuckDB/DuckLake functionality
   - `rs/dkdc-dev` - Development REPL support
   - `rs/dkdc-cli` - Main CLI application
3. **Documented each crate** with comprehensive READMEs
4. **Implemented basic functionality**:
   - SQL dev mode working with DuckDB CLI
   - Basic file/secret listing
   - Proper CLI structure with clap

### Next Steps 🚀

1. **PyO3 Integration** - Add Python interpreter support for `dkdc dev` Python mode
2. **Complete CLI Commands** - Implement remaining file, secret, archive operations  
3. **Python Wrapper** - Update `py/dkdc` to call Rust CLI
4. **Testing** - Ensure feature parity between Python and Rust versions
