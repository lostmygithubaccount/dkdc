import subprocess
import time
from pathlib import Path

import ibis
from rich.console import Console

# Configuration
console = Console()

# Constants: File paths
# WARNING: if you update these, you need to update `./bin/backup.sh` and similar
POSTGRES_DATA_PATH = Path.home() / "lake" / "data"
POSTGRES_DATA_DIR = Path.home() / "lake" / "metadata"

# Constants: Postgres configuration
# WARNING: if you update these, you need to update `./bin/backup.sh` and similar
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "dkdc"
POSTGRES_USER = "dkdc"
POSTGRES_PASSWORD = "dkdc"
POSTGRES_CONTAINER_NAME = "dkdc-dl-catalog"
MAX_POSTGRES_STARTUP_ATTEMPTS = 30
POSTGRES_STARTUP_TIMEOUT_MSG = "Postgres failed to become ready in 15 seconds"

# Constants: Schema configuration
METADATA_SCHEMAS = ["dev", "stage", "prod"]
DEFAULT_METADATA_SCHEMA = METADATA_SCHEMAS[0]


def check_duckdb() -> None:
    """Check if duckdb CLI is available and print installation help if not."""
    try:
        result = subprocess.run(["which", "duckdb"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        console.print("❌ Missing prerequisite:")
        console.print("  - duckdb CLI: curl https://install.duckdb.org | sh")
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
        console.print(
            "  - docker: https://docs.docker.com/desktop/setup/install/mac-install"
        )
        console.print("Please install docker and try again.")
        raise


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
                con = get_connection(postgres=True)
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
        raise

    # Wait for Postgres to be ready by trying to connect
    console.print("⏳ Waiting for Postgres to be ready...")
    for i in range(MAX_POSTGRES_STARTUP_ATTEMPTS):
        try:
            # Try to connect to Postgres via ducklake
            con = get_connection(postgres=True)
            con.raw_sql("SELECT 1")
            console.print("✅ Postgres is ready!")
            return
        except Exception as e:
            if i < MAX_POSTGRES_STARTUP_ATTEMPTS - 1:
                time.sleep(0.5)
            else:
                console.print(f"❌ {POSTGRES_STARTUP_TIMEOUT_MSG}")
                console.print(f"❌ Last error: {e}")
                raise


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
            raise


def _attach_schema_sql(schema: str) -> tuple[str, str]:
    """Generate SQL for attaching metadata and data connections for a schema."""
    metadata_sql = f"ATTACH 'host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}' AS metadata_{schema} (TYPE postgres, SCHEMA {schema}, READ_ONLY);"

    data_sql = f"ATTACH 'ducklake:postgres:host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_DB} user={POSTGRES_USER} password={POSTGRES_PASSWORD}' AS data_{schema} (DATA_PATH '{POSTGRES_DATA_PATH}', METADATA_SCHEMA {schema}, ENCRYPTED);"

    return metadata_sql, data_sql


def get_connection(
    postgres: bool = False, metadata_schema: str = DEFAULT_METADATA_SCHEMA
):
    """Create and return a DuckDB connection with Postgres catalog attached."""
    POSTGRES_DATA_PATH.mkdir(parents=True, exist_ok=True)

    if postgres:
        con = ibis.postgres.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=POSTGRES_DB,
            schema=metadata_schema,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
        )

    con = ibis.duckdb.connect()
    con.raw_sql(get_single_schema_sql_commands(metadata_schema))

    return con


def get_single_schema_sql_commands(
    metadata_schema: str = DEFAULT_METADATA_SCHEMA,
) -> str:
    """Generate SQL commands for single schema connection."""
    metadata_sql, data_sql = _attach_schema_sql(metadata_schema)

    return f"""
INSTALL ducklake;
INSTALL postgres;

{metadata_sql}

{data_sql}

USE data_{metadata_schema};
    """.strip()


def get_multi_schema_sql_commands(default_schema: str = DEFAULT_METADATA_SCHEMA) -> str:
    """Generate SQL commands for multi-schema connection with all schemas attached."""
    commands = [
        "INSTALL ducklake;",
        "INSTALL postgres;",
        "",
    ]

    # Add attachment commands for all schemas
    for schema in METADATA_SCHEMAS:
        metadata_sql, data_sql = _attach_schema_sql(schema)
        commands.extend([metadata_sql, "", data_sql, ""])

    # Set default schema
    commands.append(f"USE data_{default_schema};")

    return "\n".join(commands)


def get_multi_schema_connection(default_schema: str = DEFAULT_METADATA_SCHEMA):
    """Create and return a DuckDB connection with all schemas attached."""
    POSTGRES_DATA_PATH.mkdir(parents=True, exist_ok=True)

    con = ibis.duckdb.connect()

    # Install extensions
    con.raw_sql("INSTALL ducklake;")
    con.raw_sql("INSTALL postgres;")

    # Attach all schemas
    for schema in METADATA_SCHEMAS:
        metadata_sql, data_sql = _attach_schema_sql(schema)
        con.raw_sql(metadata_sql)
        con.raw_sql(data_sql)

    # Use the default schema
    con.raw_sql(f"USE data_{default_schema};")

    return con


def backup_metadata() -> None:
    """Backup Postgres metadata using pg_dump via docker exec."""
    check_docker()
    console.print("📦 Creating metadata backup...")

    try:
        # Check if container is running
        result = subprocess.run(
            ["docker", "inspect", "-f", "{{.State.Running}}", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
            text=True,
        )

        if result.stdout.strip() != "true":
            console.print("❌ Postgres container is not running")
            console.print("💡 Run './dev.py' first to start the container")
            raise RuntimeError("Postgres container not running")

        # Run pg_dump in the container and save to metadata_backup.sql
        subprocess.run(
            [
                "docker",
                "exec",
                POSTGRES_CONTAINER_NAME,
                "pg_dump",
                "-U",
                POSTGRES_USER,
                "-d",
                POSTGRES_DB,
                "-f",
                "/tmp/metadata_backup.sql",
            ],
            check=True,
            capture_output=True,
        )

        # Copy the backup file from container to host
        subprocess.run(
            [
                "docker",
                "cp",
                f"{POSTGRES_CONTAINER_NAME}:/tmp/metadata_backup.sql",
                "./metadata_backup.sql",
            ],
            check=True,
            capture_output=True,
        )

        console.print("✅ Metadata backup created: metadata_backup.sql")

    except subprocess.CalledProcessError as e:
        console.print(f"❌ Failed to create backup: {e}")
        if e.stderr:
            console.print(f"Error details: {e.stderr}")
        raise
