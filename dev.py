#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "dkdc",
# ]
# [tool.uv.sources]
# dkdc = { path = ".", editable = true }
# ///

# Prerequisites:
# - duckdb CLI (1.3.0 or later): curl https://install.duckdb.org | sh
# - uv: curl -LsSf https://astral.sh/uv/install.sh | bash
# - docker: https://docs.docker.com/desktop/setup/install/mac-install

# Imports
import subprocess

import ibis
import typer
from dkdc_dl import files, secrets
from dkdc_dl.utils import (
    DEFAULT_METADATA_SCHEMA,
    backup_metadata,
    check_docker,
    check_duckdb,
    ensure_postgres_running,
    get_connection,
    get_multi_schema_connection,
    get_multi_schema_sql_commands,
    stop_postgres,
)
from IPython import start_ipython
from rich.console import Console

# Configuration
console = Console()
app = typer.Typer(add_completion=False)


# Functions
def launch_sql_mode(metadata_schema: str = DEFAULT_METADATA_SCHEMA):
    """Launch DuckDB CLI with Postgres catalog attached."""
    check_duckdb()

    sql_cmd = get_multi_schema_sql_commands(metadata_schema)

    console.print("📦 Available: dl catalog, ducklake extension")
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")
    console.print("🔗 Connected to all schemas: dev, stage, prod")
    console.print(f"📋 Default schema: data_{metadata_schema}")

    subprocess.run(["duckdb", "-cmd", sql_cmd], check=False)


def launch_python_mode(metadata_schema: str = DEFAULT_METADATA_SCHEMA):
    """Launch IPython with Postgres catalog connection."""
    # Get multi-schema connection
    con = get_multi_schema_connection(default_schema=metadata_schema)

    # Get catalog connection for direct catalog access
    catalog_con = get_connection(postgres=True, metadata_schema=metadata_schema)

    # Configure ibis
    ibis.options.interactive = True
    ibis.options.repr.interactive.max_rows = 40
    ibis.options.repr.interactive.max_columns = None
    ibis.set_backend(con)

    # Prepare namespace
    namespace = {
        # Must-have top-level imports
        "ibis": ibis,
        # Data connections
        "con": con,
        "catalog_con": catalog_con,
        # dkdc submodules
        "utils": ibis.util,
        "files": files,
        "secrets": secrets,
    }

    console.print(f"📦 Available: {', '.join(namespace.keys())}")
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")
    console.print("🔗 Connected to all schemas: dev, stage, prod")
    console.print(f"📋 Default schema: data_{metadata_schema}")

    # Start IPython with our namespace
    start_ipython(argv=["--no-banner"], user_ns=namespace)


# Commands
@app.command()
def main(
    sql: bool = typer.Option(
        False, "--sql", help="Enter DuckDB CLI instead of IPython"
    ),
    down: bool = typer.Option(
        False, "--down", help="Stop and remove the Postgres container"
    ),
    metadata_schema: str = typer.Option(
        DEFAULT_METADATA_SCHEMA,
        "--metadata-schema",
        "-s",
        help="Metadata schema to use",
    ),
    exit_after_setup: bool = typer.Option(
        False, "--exit", help="Exit after setup without starting REPL"
    ),
    backup_metadata_flag: bool = typer.Option(
        False,
        "--backup-metadata",
        help="Create metadata backup as metadata_backup.sql and exit",
    ),
):
    """Development environment CLI with DuckLake and Postgres."""

    # Handle --down flag - stop postgres and exit
    if down:
        try:
            stop_postgres()
        except Exception:
            pass
        raise typer.Exit(0)

    # Handle --backup-metadata flag - create backup and exit
    if backup_metadata_flag:
        try:
            backup_metadata()
        except Exception as e:
            console.print(f"❌ Backup failed: {e}")
            raise typer.Exit(1)
        raise typer.Exit(0)

    # Always ensure postgres is running
    try:
        check_docker()
        ensure_postgres_running()
    except Exception as e:
        console.print(f"❌ Setup failed: {e}")
        raise typer.Exit(1)

    # Handle --exit flag
    if exit_after_setup:
        console.print("✅ Setup complete, exiting as requested")
        raise typer.Exit(0)

    mode_emoji = "🦆" if sql else "🐍"
    console.print(f"dev: {mode_emoji} (language) 🐘 (postgres)")

    try:
        if sql:
            launch_sql_mode(metadata_schema)
        else:
            launch_python_mode(metadata_schema)
    except Exception as e:
        console.print(f"❌ Failed to launch: {e}")
        raise typer.Exit(1)


# Entry point
if __name__ == "__main__":
    app()
