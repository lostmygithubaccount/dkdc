import subprocess
import time

import ibis
from rich.console import Console

from dkdc.config import (
    DEFAULT_METADATA_SCHEMA,
    DOCKER_INSTALL_URL,
    DOCKER_POSTGRES_IMAGE,
    DOCKER_RESTART_POLICY,
    DUCKDB_INSTALL_URL,
    DUCKLAKE_EXTENSION,
    MAX_POSTGRES_STARTUP_ATTEMPTS,
    METADATA_SCHEMAS,
    POSTGRES_CONTAINER_NAME,
    POSTGRES_DATA_DIR,
    POSTGRES_DATA_PATH,
    POSTGRES_DB,
    POSTGRES_EXTENSION,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_STARTUP_TIMEOUT_MSG,
    POSTGRES_USER,
)

# Configuration
console = Console()


def check_duckdb() -> None:
    """Check if duckdb CLI is available and print installation help if not."""
    try:
        result = subprocess.run(["which", "duckdb"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        console.print("❌ Missing prerequisite:")
        console.print(f"  - duckdb CLI: {DUCKDB_INSTALL_URL}")
        console.print("Please install duckdb CLI and try again.")
        raise


def check_docker():
    """Check if docker is available and print installation help if not."""
    try:
        result = subprocess.run(["which", "docker"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        console.print("❌ Missing prerequisite:")
        console.print(f"  - docker: {DOCKER_INSTALL_URL}")
        console.print("Please install docker and try again.")
        raise


def ensure_postgres_running(quiet: bool = False):
    """Ensure Postgres container is running and ready."""
    if not quiet:
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
            if not quiet:
                console.print("✅ Postgres container already running")
            # Test connection to ensure it's ready
            try:
                con = get_postgres_connection()
                con.raw_sql("SELECT 1")
                if not quiet:
                    console.print("✅ Postgres is ready!")
                return
            except Exception as e:
                if not quiet:
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
            if not quiet:
                console.print(
                    "🔄 Existing container found but not running, removing..."
                )
            subprocess.run(
                ["docker", "rm", POSTGRES_CONTAINER_NAME],
                check=True,
                capture_output=True,
            )
            if not quiet:
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
                DOCKER_RESTART_POLICY,
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
                DOCKER_POSTGRES_IMAGE,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        if not quiet:
            console.print("✅ Postgres container started")
    except subprocess.CalledProcessError as e:
        if not quiet:
            console.print(f"❌ Failed to start Postgres container: {e}")
            if e.stderr:
                console.print(f"Error details: {e.stderr}")
            if e.stdout:
                console.print(f"Output: {e.stdout}")
            console.print(
                "💡 Try running './dev.py --down' first to clean up any existing containers"
            )
        raise

    # Wait for Postgres to be ready by trying to connect
    if not quiet:
        console.print("⏳ Waiting for Postgres to be ready...")
    for i in range(MAX_POSTGRES_STARTUP_ATTEMPTS):
        try:
            # Try to connect to Postgres via ducklake
            con = get_postgres_connection()
            con.raw_sql("SELECT 1")
            if not quiet:
                console.print("✅ Postgres is ready!")
            return
        except Exception as e:
            if i < MAX_POSTGRES_STARTUP_ATTEMPTS - 1:
                time.sleep(0.5)
            else:
                if not quiet:
                    console.print(f"❌ {POSTGRES_STARTUP_TIMEOUT_MSG}")
                    console.print(f"❌ Last error: {e}")
                raise


def stop_postgres(quiet: bool = False):
    """Stop and remove the Postgres container."""
    check_docker()
    if not quiet:
        console.print("🛑 Stopping Postgres container...")

    try:
        # Stop the container
        subprocess.run(
            ["docker", "stop", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
        )
        if not quiet:
            console.print("✅ Postgres container stopped")

        # Remove the container
        subprocess.run(
            ["docker", "rm", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
        )
        if not quiet:
            console.print("✅ Postgres container removed")

    except subprocess.CalledProcessError as e:
        if "No such container" in str(e.stderr):
            if not quiet:
                console.print("✅ Postgres container was not running")
        else:
            if not quiet:
                console.print(f"❌ Failed to stop Postgres container: {e}")
                if e.stderr:
                    console.print(f"Error details: {e.stderr}")
            raise


def _attach_schema_sql(schema: str) -> tuple[str, str]:
    """Generate SQL for attaching metadata and data connections for a schema."""
    metadata_sql = f"ATTACH 'host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}' AS metadata_{schema} (TYPE postgres, SCHEMA {schema}, READ_ONLY);"

    data_sql = f"ATTACH 'ducklake:postgres:host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}' AS data_{schema} (DATA_PATH '{POSTGRES_DATA_PATH}', METADATA_SCHEMA {schema}, ENCRYPTED);"

    return metadata_sql, data_sql


def get_postgres_connection(metadata_schema: str = DEFAULT_METADATA_SCHEMA):
    """Create and return a DuckDB connection with Postgres catalog attached."""
    POSTGRES_DATA_PATH.mkdir(parents=True, exist_ok=True)

    con = ibis.postgres.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        schema=metadata_schema,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
    return con


def get_single_schema_sql_commands(
    metadata_schema: str = DEFAULT_METADATA_SCHEMA,
) -> str:
    """Generate SQL commands for single schema connection."""
    metadata_sql, data_sql = _attach_schema_sql(metadata_schema)

    return f"""
INSTALL {DUCKLAKE_EXTENSION};
INSTALL {POSTGRES_EXTENSION};

{metadata_sql}

{data_sql}

USE data_{metadata_schema};
    """.strip()


def get_multi_schema_sql_commands(default_schema: str = DEFAULT_METADATA_SCHEMA) -> str:
    """Generate SQL commands for multi-schema connection with all schemas attached."""
    commands = [
        f"INSTALL {DUCKLAKE_EXTENSION};",
        f"INSTALL {POSTGRES_EXTENSION};",
        "",
    ]

    # Add attachment commands for all schemas
    for schema in METADATA_SCHEMAS:
        metadata_sql, data_sql = _attach_schema_sql(schema)
        commands.extend([metadata_sql, "", data_sql, ""])

    # Set default schema
    commands.append(f"USE data_{default_schema};")

    return "\n".join(commands)


def get_duckdb_connection(default_schema: str = DEFAULT_METADATA_SCHEMA):
    """Create and return a DuckDB connection with all schemas attached."""
    POSTGRES_DATA_PATH.mkdir(parents=True, exist_ok=True)

    con = ibis.duckdb.connect()

    # Install extensions
    con.raw_sql(f"INSTALL {DUCKLAKE_EXTENSION};")
    con.raw_sql(f"INSTALL {POSTGRES_EXTENSION};")

    # Attach all schemas
    for schema in METADATA_SCHEMAS:
        metadata_sql, data_sql = _attach_schema_sql(schema)
        con.raw_sql(metadata_sql)
        con.raw_sql(data_sql)

    # Use the default schema
    con.raw_sql(f"USE data_{default_schema};")

    return con
