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
import time
from pathlib import Path

import duckdb  # noqa
import ibis
import pandas as pd  # noqa
import polars as pl  # noqa
import typer
from IPython import start_ipython
from rich.console import Console

# Configuration
console = Console()
app = typer.Typer(add_completion=False)

# Constants: File paths
POSTGRES_DATA_PATH = Path.home() / "lake" / "data"
POSTGRES_DATA_DIR = Path.home() / "lake" / "metadata"

# Constants: Postgres configuration
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "dkdc"
POSTGRES_USER = "dkdc"
POSTGRES_PASSWORD = "dkdc"
POSTGRES_CONTAINER_NAME = "dkdc-dl-catalog"
MAX_POSTGRES_STARTUP_ATTEMPTS = 30
POSTGRES_STARTUP_TIMEOUT_MSG = "Postgres failed to become ready in 15 seconds"

# Constants: Schema configuration
SCHEMAS = ["dev", "stage", "prod"]
DEFAULT_METADATA_SCHEMA = SCHEMAS[0]

# SQL command templates
POSTGRES_SQL_COMMANDS = """
-- Install extensions
INSTALL ducklake;
INSTALL postgres;

-- Attach metadata connection
ATTACH 'host={host} port={port} dbname={database} user={user} password={password}' AS metadata (TYPE postgres, SCHEMA {metadata_schema}, READ_ONLY);

-- Attach data connection
ATTACH 'ducklake:postgres:host={host} port={port} dbname={database} user={user} password={password}'
    AS data (DATA_PATH '{data_path}', METADATA_SCHEMA {metadata_schema}, ENCRYPTED); 

-- Use data connection
USE data;
""".strip()


# Functions
def check_duckdb():
    """Check if duckdb CLI is available and print installation help if not."""
    try:
        result = subprocess.run(["which", "duckdb"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        console.print("❌ Missing prerequisite:")
        console.print("  - duckdb CLI: curl https://install.duckdb.org | sh")
        console.print("Please install duckdb CLI and try again.")
        raise typer.Exit(1)


def check_docker():
    """Check if docker is available and print installation help if not."""
    try:
        result = subprocess.run(["which", "docker"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        console.print("❌ Missing prerequisite:")
        console.print(
            "  - docker: https://docs.docker.com/desktop/setup/install/mac-install"
        )
        console.print("Please install docker and try again.")
        raise typer.Exit(1)


def get_postgres_connection(
    catalog: bool = False, metadata_schema: str = DEFAULT_METADATA_SCHEMA
):
    """Create and return a DuckDB connection with Postgres catalog attached."""
    POSTGRES_DATA_PATH.mkdir(parents=True, exist_ok=True)

    if not catalog:
        con = ibis.duckdb.connect()
        con.raw_sql(
            POSTGRES_SQL_COMMANDS.format(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                database=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                data_path=POSTGRES_DATA_PATH,
                metadata_schema=metadata_schema,
            )
        )
    else:
        con = ibis.postgres.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            schema=metadata_schema,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

    return con


def ensure_postgres_running():
    """Ensure Postgres container is running and ready."""
    console.print("📦 Checking Postgres container...")

    # Ensure both lake directories exist
    POSTGRES_DATA_PATH.mkdir(parents=True, exist_ok=True)
    POSTGRES_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check if container already exists and is running
    try:
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout.strip() == "true":
            console.print("✅ Postgres container already running")
            # Test connection to ensure it's ready
            try:
                con = get_postgres_connection()
                con.raw_sql("SELECT 1")
                console.print("✅ Postgres is ready!")
                return
            except Exception as e:
                console.print(f"⚠️ Container running but not responding: {e}")
                console.print("Will restart container...")
                # Stop and remove the unresponsive container
                subprocess.run(
                    ["docker", "stop", POSTGRES_CONTAINER_NAME],
                    check=True,
                    capture_output=True,
                )
                subprocess.run(
                    ["docker", "rm", POSTGRES_CONTAINER_NAME],
                    check=True,
                    capture_output=True,
                )
        else:
            # Container exists but not running, remove it
            console.print("🔄 Existing container found but not running, removing...")
            subprocess.run(
                ["docker", "rm", POSTGRES_CONTAINER_NAME],
                check=True,
                capture_output=True,
            )
            console.print("✅ Existing container removed")
    except subprocess.CalledProcessError:
        # Container doesn't exist, which is fine
        pass

    try:
        # Start postgres container directly with docker
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--name",
                POSTGRES_CONTAINER_NAME,
                "--restart",
                "unless-stopped",
                "-e",
                f"POSTGRES_DB={POSTGRES_DB}",
                "-e",
                f"POSTGRES_USER={POSTGRES_USER}",
                "-e",
                f"POSTGRES_PASSWORD={POSTGRES_PASSWORD}",
                "-p",
                f"{POSTGRES_PORT}:{POSTGRES_PORT}",
                "-v",
                f"{POSTGRES_DATA_DIR.absolute()}:/var/lib/postgresql/data",
                "postgres:latest",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        console.print("✅ Postgres container started")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to start Postgres container: {e}")
        if e.stderr:
            console.print(f"Error details: {e.stderr}")
        if e.stdout:
            console.print(f"Output: {e.stdout}")
        console.print(
            "💡 Try running './dev.py --down' first to clean up any existing containers"
        )
        raise typer.Exit(1)

    # Wait for Postgres to be ready by trying to connect
    console.print("⏳ Waiting for Postgres to be ready...")
    for i in range(MAX_POSTGRES_STARTUP_ATTEMPTS):
        try:
            # Try to connect to Postgres via ducklake
            con = get_postgres_connection()
            con.raw_sql("SELECT 1")
            console.print("✅ Postgres is ready!")
            return
        except Exception as e:
            if i < MAX_POSTGRES_STARTUP_ATTEMPTS - 1:
                time.sleep(0.5)
            else:
                console.print(f"❌ {POSTGRES_STARTUP_TIMEOUT_MSG}")
                console.print(f"❌ Last error: {e}")
                raise typer.Exit(1)


def stop_postgres():
    """Stop and remove the Postgres container."""
    check_docker()
    console.print("🛑 Stopping Postgres container...")

    try:
        # Stop the container
        subprocess.run(
            ["docker", "stop", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
        )
        console.print("✅ Postgres container stopped")

        # Remove the container
        subprocess.run(
            ["docker", "rm", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
        )
        console.print("✅ Postgres container removed")

    except subprocess.CalledProcessError as e:
        if "No such container" in str(e.stderr):
            console.print("✅ Postgres container was not running")
        else:
            console.print(f"❌ Failed to stop Postgres container: {e}")
            if e.stderr:
                console.print(f"Error details: {e.stderr}")
            raise typer.Exit(1)


def run_command(command: list[str]):
    """Run a command and print it."""
    console.print(f"Running: {' '.join(command)}")
    subprocess.run(command, check=False)


def launch_sql_mode(metadata_schema: str = DEFAULT_METADATA_SCHEMA):
    """Launch DuckDB CLI with Postgres catalog attached."""
    check_duckdb()

    sql_cmd = POSTGRES_SQL_COMMANDS.format(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        data_path=POSTGRES_DATA_PATH,
        metadata_schema=metadata_schema,
    )

    console.print("📦 Available: dl catalog, ducklake extension")
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")

    subprocess.run(["duckdb", "-cmd", sql_cmd], check=False)


def launch_python_mode(metadata_schema: str = DEFAULT_METADATA_SCHEMA):
    """Launch IPython with Postgres catalog connection."""
    # Get connection
    con = get_postgres_connection(catalog=False, metadata_schema=metadata_schema)

    # Get catalog connection for direct catalog access
    catalog_con = get_postgres_connection(catalog=True, metadata_schema=metadata_schema)

    # Configure ibis
    ibis.options.interactive = True
    ibis.options.repr.interactive.max_rows = 40
    ibis.options.repr.interactive.max_columns = None
    ibis.set_backend(con)

    # Prepare namespace
    namespace = {
        "con": con,
        "catalog_con": catalog_con,
        "ibis": ibis,
    }

    console.print(f"📦 Available: {', '.join(namespace.keys())}")
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")

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
):
    """Development environment CLI with DuckLake and Postgres."""

    # Handle --down flag - stop postgres and exit
    if down:
        stop_postgres()
        raise typer.Exit(0)

    # Always ensure postgres is running
    check_docker()
    ensure_postgres_running()

    # Handle --exit flag
    if exit_after_setup:
        console.print("✅ Setup complete, exiting as requested")
        raise typer.Exit(0)

    mode_emoji = "🦆" if sql else "🐍"
    console.print(f"dev: {mode_emoji} (language) 🐘 (postgres)")

    if sql:
        launch_sql_mode(metadata_schema)
    else:
        launch_python_mode(metadata_schema)


# Entry point
if __name__ == "__main__":
    app()
