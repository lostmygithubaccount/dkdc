"""Database connection utilities for dkdc."""

import subprocess

import ibis

from dkdc.config import (
    DATA_DB_NAME,
    DATA_PATH,
    DUCKLAKE_EXTENSION,
    SQLITE_EXTENSION,
    SQLITE_METADATA_PATH,
)


def check_duckdb() -> bool:
    """Check if duckdb CLI is available."""
    try:
        result = subprocess.run(["which", "duckdb"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def ensure_setup() -> None:
    """Ensure directories exist."""
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    SQLITE_METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_metadata_connection():
    """Get SQLite connection to metadata database."""
    ensure_setup()
    return ibis.sqlite.connect(str(SQLITE_METADATA_PATH))


def get_duckdb_connection():
    """Get DuckDB connection with DuckLake and metadata attached."""
    ensure_setup()

    con = ibis.duckdb.connect()

    # Install extensions
    con.raw_sql(f"INSTALL {DUCKLAKE_EXTENSION};")
    con.raw_sql(f"INSTALL {SQLITE_EXTENSION};")

    # Attach SQLite metadata database
    con.raw_sql(f"ATTACH '{SQLITE_METADATA_PATH}' AS metadata;")

    # Attach DuckLake data database
    con.raw_sql(
        f"ATTACH 'ducklake:sqlite:{SQLITE_METADATA_PATH}' AS {DATA_DB_NAME} (DATA_PATH '{DATA_PATH}', ENCRYPTED);"
    )
    con.raw_sql(f"USE {DATA_DB_NAME};")

    return con


def get_sql_commands() -> str:
    """Get SQL commands for CLI setup."""
    return f"""
INSTALL {DUCKLAKE_EXTENSION};
INSTALL {SQLITE_EXTENSION};

ATTACH '{SQLITE_METADATA_PATH}' AS metadata;
ATTACH 'ducklake:sqlite:{SQLITE_METADATA_PATH}' AS {DATA_DB_NAME} (DATA_PATH '{DATA_PATH}', ENCRYPTED);

USE {DATA_DB_NAME};
    """.strip()
