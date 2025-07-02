# dkdc-py

Python extension module that bridges Python and Rust for dkdc.

## What This Is

This crate is the magic that makes `dkdc` work as a Python package. It:

1. Uses PyO3 to create Python bindings for all Rust functionality
2. Compiles to a module named `_dkdc` that Python imports
3. Provides native Python functions that call into Rust code
4. Handles all type conversions between Python and Rust

## How It Works

When you run `dkdc` from Python:

```
User → Python CLI (py/dkdc/cli/main.py) → imports _dkdc → Rust code executes
```

This is NOT a subprocess call - it's direct Python→Rust function calls, which means:
- Native performance (no process overhead)
- Proper error handling
- Clean type conversions
- Single binary distribution

## Exported Functions

The module exports these Python functions:

- `run_cli(args)` - Main CLI entry point
- `list_files(path)` - List files in virtual filesystem
- `add_file(file_path, virtual_path)` - Add file to data lake
- `get_secret(name)` - Retrieve a secret
- `set_secret(name, value, force)` - Store a secret
- `list_secrets()` - List all secrets
- `delete_secret(name)` - Remove a secret
- `launch_dev(sql_mode)` - Launch development REPL
- `get_connection_string()` - Get DuckDB connection info

## Building

This crate is built automatically when you:

```bash
# Development build
uv run maturin develop

# Release build
uv run maturin build --release
```

The resulting module is packaged into the Python wheel along with the Python code.

## Why This Architecture?

1. **Performance**: Rust speed with Python convenience
2. **Distribution**: Single wheel includes everything
3. **Type Safety**: PyO3 ensures proper conversions
4. **No Dependencies**: Users don't need Rust installed

## Development Notes

- This crate is excluded from the Rust workspace because it has special build requirements
- It depends on all the core dkdc crates to provide functionality
- The Python code in `py/` is just a thin wrapper around this module
- Changes here require running `maturin develop` to see in Python