#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ascend-product",
# ]
# [tool.uv.sources]
# ascend-product = { path = ".", editable = true }
# ///

# Prerequisites:
# - duckdb CLI (1.3.0 or later): curl https://install.duckdb.org | sh
# - uv: curl -LsSf https://astral.sh/uv/install.sh | bash
# - docker: https://docs.docker.com/desktop/setup/install/mac-install

# Imports
import os
import sqlite3  # noqa
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

# Constants - File paths
SQLITE_DATA_PATH = Path("datalake/catalog-sqlite")
SQLITE_CATALOG_PATH = "catalog.sqlite"
POSTGRES_DATA_PATH = Path("datalake/catalog-postgres")
POSTGRES_DATA_DIR = Path("catalog.postgres")
CSV_DATA_PATH = Path("penguins.csv")
DELTA_DATA_PATH = Path("penguins.delta")
PARQUET_DATA_PATH = Path("penguins.parquet")
BOOTSTRAP_MARKER = Path(".DEMO_BOOTSTRAP")

# Constants - Data sources
BUCKET = "gs://ascend-io-gcs-public"
FEEDBACK_ASCENDERS_GLOB = "ottos-expeditions/lakev0/generated/events/feedback_ascenders.parquet/year=*/month=*/day=*/*.parquet"

# Constants - Postgres configuration
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "ducklake"
POSTGRES_USER = "product"
POSTGRES_PASSWORD = "product"
POSTGRES_CONTAINER_NAME = "product-dl-catalog"
MAX_POSTGRES_STARTUP_ATTEMPTS = 30
POSTGRES_STARTUP_TIMEOUT_MSG = "Postgres failed to become ready in 15 seconds"

# Constants - Schema configuration
SCHEMAS = [
    "default",
    "workspace_cody",
    "workspace_otto",
    "deployment_development",
    "deployment_staging",
    "deployment_production",
]

# SQL command templates
SQLITE_SQL_COMMANDS = """
INSTALL ducklake;
INSTALL sqlite;
ATTACH 'ducklake:sqlite:{catalog_path}'
    AS dl (DATA_PATH '{data_path}');
USE dl;
""".strip()

POSTGRES_SQL_COMMANDS = """
INSTALL ducklake;
INSTALL postgres;
ATTACH 'ducklake:postgres:host={host} port={port} dbname={database} user={user} password={password}'
    AS dl (DATA_PATH '{data_path}', METADATA_SCHEMA '{metadata_schema}'); 
USE dl;
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


def get_sqlite_connection(catalog: bool = False, metadata_schema: str = "default"):
    """Create and return a DuckDB connection with SQLite catalog attached."""
    SQLITE_DATA_PATH.mkdir(parents=True, exist_ok=True)

    if not catalog:
        con = ibis.duckdb.connect()
        con.raw_sql(
            SQLITE_SQL_COMMANDS.format(
                catalog_path=SQLITE_CATALOG_PATH, data_path=SQLITE_DATA_PATH
            )
        )
    else:
        con = ibis.sqlite.connect(str(SQLITE_CATALOG_PATH))

    return con


def get_postgres_connection(catalog: bool = False, metadata_schema: str = "default"):
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

    # Ensure pgdata directory exists
    POSTGRES_DATA_DIR.mkdir(exist_ok=True)

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


def safe_remove(path: str | Path):
    """Safely remove a file or directory if it exists."""
    path_obj = Path(path)
    if path_obj.exists():
        if path_obj.is_dir():
            run_command(["rm", "-rf", str(path_obj)])
        else:
            run_command(["rm", "-f", str(path_obj)])
    else:
        console.print(f"Skipping {path} (does not exist)")


def clean_demo():
    """Clean up demo data and containers."""
    console.print("🧹 Cleaning up demo data...")

    # Stop postgres first
    stop_postgres()

    # Remove demo files and directories
    safe_remove("catalog.sqlite")
    safe_remove("catalog.postgres")
    safe_remove("datalake")
    safe_remove("penguins.delta")
    safe_remove(".DEMO_BOOTSTRAP")

    console.print("✅ Demo cleanup complete")


def bootstrap_demo():
    """Bootstrap demo data: penguins tables, feedback_ascenders data, and delta files."""
    if BOOTSTRAP_MARKER.exists():
        console.print("✅ Demo already bootstrapped (found .DEMO_BOOTSTRAP file)")
        return

    console.print("🚀 Bootstrapping DuckLake demo data...")

    # Ensure Postgres is running
    check_docker()
    ensure_postgres_running()

    # Setup SQLite data (SQLite doesn't support METADATA_SCHEMA, so just use default)
    console.print("📊 Setting up SQLite data...")
    con = get_sqlite_connection()
    ibis.set_backend(con)

    t = ibis.read_parquet(f"{BUCKET}/{FEEDBACK_ASCENDERS_GLOB}")
    con.create_table("feedback_ascenders", t, overwrite=True)
    console.print(f"✅ SQLite setup complete. Tables: {con.list_tables()}")

    # Setup Postgres data (now uses penguins data)
    console.print("📊 Setting up Postgres data...")
    for schema in SCHEMAS:
        console.print(f"  Setting up Postgres schema: {schema}")
        con = get_postgres_connection(metadata_schema=schema)
        ibis.set_backend(con)

        t = ibis.examples.penguins.fetch()
        con.create_table("penguins", t, overwrite=True)
        con.create_table("penguins2", t, overwrite=True)
        console.print(
            f"    ✅ Postgres {schema} setup complete. Tables: {con.list_tables()}"
        )

    # Setup CSV files
    console.print("📊 Setting up CSV files...")
    penguins = ibis.examples.penguins.fetch()
    penguins.to_csv(str(CSV_DATA_PATH), overwrite=True)
    console.print("✅ CSV files setup complete")

    # Setup Delta files
    console.print("📊 Setting up Delta files...")
    penguins = ibis.examples.penguins.fetch()
    penguins.to_delta(str(DELTA_DATA_PATH), mode="overwrite")
    penguins.to_delta(str(DELTA_DATA_PATH), mode="overwrite")
    penguins.to_delta(str(DELTA_DATA_PATH), mode="overwrite")
    penguins.to_delta(str(DELTA_DATA_PATH), mode="overwrite")
    penguins.to_delta(str(DELTA_DATA_PATH), mode="overwrite")
    penguins.to_delta(str(DELTA_DATA_PATH), mode="overwrite")
    penguins.to_delta(str(DELTA_DATA_PATH), mode="overwrite")
    console.print("✅ Delta files setup complete")

    # Setup Parquet files
    console.print("📊 Setting up Parquet files...")
    penguins = ibis.examples.penguins.fetch()
    penguins.to_parquet(str(PARQUET_DATA_PATH), overwrite=True)
    console.print("✅ Parquet files setup complete")

    # Create bootstrap marker file
    BOOTSTRAP_MARKER.touch()
    console.print("🎉 Demo bootstrap complete!")


def launch_sql_mode(catalog: str, metadata_schema: str = "default"):
    """Launch DuckDB CLI with appropriate catalog attached."""
    check_duckdb()

    if catalog == "postgres":
        sql_cmd = POSTGRES_SQL_COMMANDS.format(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            data_path=POSTGRES_DATA_PATH,
            metadata_schema=metadata_schema,
        )
    else:
        sql_cmd = SQLITE_SQL_COMMANDS.format(
            catalog_path=SQLITE_CATALOG_PATH, data_path=SQLITE_DATA_PATH
        )

    console.print("📦 Available: dl catalog, ducklake extension")
    console.print(f"🌍 PRODUCT_DL_CATALOG={catalog}")
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")

    subprocess.run(["duckdb", "-cmd", sql_cmd], check=False)


def launch_python_mode(catalog: str, metadata_schema: str = "default"):
    """Launch IPython with appropriate catalog connection."""
    # Set environment
    os.environ["PRODUCT_DL_CATALOG"] = catalog

    # Get connection based on catalog type
    con = (
        get_postgres_connection(metadata_schema=metadata_schema)
        if catalog == "postgres"
        else get_sqlite_connection(metadata_schema=metadata_schema)
    )

    # Get catalog connection for direct catalog access
    catalog_con = (
        get_postgres_connection(catalog=True)
        if catalog == "postgres"
        else get_sqlite_connection(catalog=True)
    )

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
        "bucket": BUCKET,
        "feedback_ascenders_glob": FEEDBACK_ASCENDERS_GLOB,
    }

    console.print(f"📦 Available: {', '.join(namespace.keys())}")
    console.print(
        f"🌍 PRODUCT_DL_CATALOG={os.environ.get('PRODUCT_DL_CATALOG', 'unset')}"
    )
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")

    # Start IPython with our namespace
    start_ipython(argv=["--no-banner"], user_ns=namespace)


# Commands
@app.command()
def main(
    sql: bool = typer.Option(
        False, "--sql", help="Enter DuckDB CLI instead of IPython"
    ),
    catalog: str = typer.Option(
        "sqlite", "--catalog", help="Catalog type: sqlite or postgres"
    ),
    postgres: bool = typer.Option(
        False,
        "--postgres",
        help="Use postgres catalog (equivalent to --catalog postgres)",
    ),
    down: bool = typer.Option(
        False, "--down", help="Stop and remove the Postgres container"
    ),
    clean: bool = typer.Option(
        False, "--clean", help="Clean up demo data and stop containers"
    ),
    metadata_schema: str = typer.Option(
        "default", "--metadata-schema", "-s", help="Metadata schema to use"
    ),
    exit_after_setup: bool = typer.Option(
        False, "--exit", help="Exit after setup without starting REPL"
    ),
    restart: bool = typer.Option(
        False,
        "--restart",
        help="Reset all state: clean up, bootstrap fresh, then exit (equivalent to --clean && --exit)",
    ),
):
    """Ascend product development environment CLI with DuckLake."""

    # Handle --restart flag - clean up demo data, then continue with setup but exit
    if restart:
        clean_demo()
        exit_after_setup = True  # Force exit after setup

    # Handle --down flag - stop postgres and exit
    if down:
        stop_postgres()
        raise typer.Exit(0)

    # Handle --clean flag - clean up demo data and exit
    if clean:
        clean_demo()
        raise typer.Exit(0)

    # Handle --postgres flag
    if postgres:
        catalog = "postgres"

    # Validate metadata schema usage with SQLite
    if catalog.lower() == "sqlite" and metadata_schema != "default":
        console.print(
            "⚠️  Warning: SQLite catalog does not support METADATA_SCHEMA parameter"
        )
        console.print(
            f"   Requested schema '{metadata_schema}' will be ignored, using 'default' instead"
        )
        metadata_schema = "default"

    # Bootstrap demo if never bootstrapped before
    if not BOOTSTRAP_MARKER.exists():
        bootstrap_demo()

    # Always ensure postgres is running when using postgres catalog
    if catalog.lower() == "postgres":
        check_docker()
        ensure_postgres_running()

    os.environ["PRODUCT_DL_CATALOG"] = catalog.lower()

    # Handle --exit flag
    if exit_after_setup:
        console.print("✅ Setup complete, exiting as requested")
        raise typer.Exit(0)

    catalog_emoji = "🐘" if catalog.lower() == "postgres" else "🗂️"
    mode_emoji = "🦆" if sql else "🐍"
    console.print(f"product dev: {mode_emoji} (language) {catalog_emoji} (catalog)")

    if sql:
        launch_sql_mode(catalog.lower(), metadata_schema)
    else:
        launch_python_mode(catalog.lower(), metadata_schema)


# Entry point
if __name__ == "__main__":
    app()
