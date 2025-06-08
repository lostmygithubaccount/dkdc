import subprocess
import time

import ibis

from dkdc.config import (
    DEFAULT_METADATA_SCHEMA,
    DOCKER_POSTGRES_IMAGE,
    DOCKER_RESTART_POLICY,
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
    POSTGRES_USER,
)


def check_duckdb() -> bool:
    """Check if duckdb CLI is available."""
    try:
        result = subprocess.run(["which", "duckdb"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_docker() -> bool:
    """Check if docker is available."""
    try:
        result = subprocess.run(["which", "docker"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def ensure_postgres_running() -> None:
    """Ensure Postgres container is running and ready."""
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
            # Test connection to ensure it's ready
            try:
                con = get_postgres_connection()
                con.raw_sql("SELECT 1")
                return
            except Exception:
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
            subprocess.run(
                ["docker", "rm", POSTGRES_CONTAINER_NAME],
                check=True,
                capture_output=True,
            )
    except subprocess.CalledProcessError:
        # Container doesn't exist, which is fine
        pass

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

    # Wait for Postgres to be ready by trying to connect
    for i in range(MAX_POSTGRES_STARTUP_ATTEMPTS):
        try:
            # Try to connect to Postgres via ducklake
            con = get_postgres_connection()
            con.raw_sql("SELECT 1")
            return
        except Exception as e:
            if i < MAX_POSTGRES_STARTUP_ATTEMPTS - 1:
                time.sleep(0.5)
            else:
                raise RuntimeError(
                    f"Postgres failed to start after {MAX_POSTGRES_STARTUP_ATTEMPTS} attempts: {e}"
                )


def stop_postgres() -> None:
    """Stop and remove the Postgres container."""
    if not check_docker():
        raise RuntimeError("Docker is not available")

    try:
        # Stop the container
        subprocess.run(
            ["docker", "stop", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
        )

        # Remove the container
        subprocess.run(
            ["docker", "rm", POSTGRES_CONTAINER_NAME],
            check=True,
            capture_output=True,
        )

    except subprocess.CalledProcessError as e:
        if "No such container" not in str(e.stderr):
            raise RuntimeError(f"Failed to stop Postgres container: {e}")


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
