# Imports
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import ibis
import ibis.expr.datatypes as dt

from dkdc.config import (
    FILES_TABLE_NAME,
)

# Constants: Standard file-based table schema
FILE_TABLE_SCHEMA = ibis.schema(
    {
        "filepath": str,
        "filename": str,
        "filedata": dt.binary,
        "filesize": int,
        "fileupdated": dt.timestamp,
    }
)

# Default table configuration
TABLE_NAME = FILES_TABLE_NAME
TABLE_SCHEMA = FILE_TABLE_SCHEMA


# Generic Functions: These work with any table using the file schema
def ensure_file_table(
    con: ibis.BaseBackend,
    table_name: str,
    table_schema: Optional[ibis.Schema] = None,
) -> None:
    """Ensure a file-based table exists.

    Args:
        con: Database connection
        table_name: Name of the table to ensure exists
        table_schema: Optional custom schema. If None, uses FILE_TABLE_SCHEMA.
    """
    if table_schema is None:
        table_schema = FILE_TABLE_SCHEMA

    # Check if table exists
    if table_name not in con.list_tables():
        # Create the table
        con.create_table(table_name, schema=table_schema)


def _add_file_to_table(
    con: ibis.BaseBackend,
    table_name: str,
    filepath: str,
    filename: str,
    filedata: bytes,
) -> str:
    """Internal function to add file data to a specific table. Returns the filename.

    Args:
        con: Database connection
        table_name: Name of the table to insert into
        filepath: Virtual path in the datalake
        filename: Name of the file
        filedata: Binary file data
    """
    ensure_file_table(con, table_name)

    now = datetime.now(UTC)
    data = {
        "filepath": [filepath],
        "filename": [filename],
        "filedata": [filedata],
        "filesize": [len(filedata)],
        "fileupdated": [now],
    }

    con.insert(table_name, data)
    return filename


def add_file_to_table(
    con: ibis.BaseBackend,
    table_name: str,
    file_path: Union[str, Path],
    filepath: Optional[str] = None,
    filename: Optional[str] = None,
) -> str:
    """Add a file to a specific table. Returns the filename.

    Args:
        con: Database connection
        table_name: Name of the table to insert into
        file_path: Path to the file to add
        filepath: Optional virtual path in the datalake. If None, uses "./files".
        filename: Optional custom filename. If None, uses the actual filename.
    """
    file_path = Path(file_path).expanduser()

    # Use provided filepath or default to "./files"
    if filepath is None:
        filepath = "./files"

    # Use provided filename or actual filename
    if filename is None:
        filename = file_path.name

    filedata = file_path.read_bytes()

    return _add_file_to_table(con, table_name, filepath, filename, filedata)


# Legacy Functions: Maintained for backward compatibility
def ensure_files_table(con: ibis.BaseBackend) -> None:
    """Ensure the files table exists."""
    ensure_file_table(con, TABLE_NAME)


def add_file(
    con: ibis.BaseBackend,
    file_path: Union[str, Path],
    filepath: Optional[str] = None,
    filename: Optional[str] = None,
) -> str:
    """Add a file to the files table. Returns the filename.

    Args:
        con: Database connection
        file_path: Path to the file to add
        filepath: Optional virtual path in the datalake. If None, uses "./files".
        filename: Optional custom filename. If None, uses the actual filename.
    """
    return add_file_to_table(con, TABLE_NAME, file_path, filepath, filename)


def _add_file(
    con: ibis.BaseBackend,
    filepath: str,
    filename: str,
    filedata: bytes,
) -> str:
    """Internal function to add file data directly. Returns the filename."""
    return _add_file_to_table(con, TABLE_NAME, filepath, filename, filedata)


# File Retrieval Functions
def get_file_from_table(
    con: ibis.BaseBackend,
    table_name: str,
    filename: str,
    filepath: Optional[str] = None,
    latest: bool = True,
) -> Optional[Dict[str, Any]]:
    """Retrieve a file from a specific table.

    Args:
        con: Database connection
        table_name: Name of the table to query
        filename: Name of the file to retrieve
        filepath: Optional filepath filter. If None, uses "./files".
        latest: If True, returns only the most recent version

    Returns:
        Dictionary with file data or None if not found
    """
    ensure_file_table(con, table_name)

    # Default filepath
    if filepath is None:
        filepath = "./files"

    table = con.table(table_name)

    query = table.filter((ibis._["filename"] == filename)).filter(
        ibis._["filepath"] == filepath
    )

    if latest:
        query = query.order_by(ibis._["fileupdated"].desc()).limit(1)

    result = query.to_pyarrow().to_pylist()

    if not result:
        return None

    return result[0] if latest else result


def get_file_data_from_table(
    con: ibis.BaseBackend,
    table_name: str,
    filename: str,
    filepath: Optional[str] = None,
) -> Optional[bytes]:
    """Retrieve just the file data (bytes) from a specific table.

    Args:
        con: Database connection
        table_name: Name of the table to query
        filename: Name of the file to retrieve
        filepath: Optional filepath filter. If None, uses "./files".

    Returns:
        File data as bytes or None if not found
    """
    result = get_file_from_table(con, table_name, filename, filepath, latest=True)
    return result["filedata"] if result else None


# Convenience functions for specific tables
def get_file(
    con: ibis.BaseBackend,
    filename: str,
    filepath: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve a file from the files table."""
    return get_file_from_table(con, TABLE_NAME, filename, filepath)


def get_file_data(
    con: ibis.BaseBackend,
    filename: str,
    filepath: Optional[str] = None,
) -> Optional[bytes]:
    """Retrieve just the file data from the files table."""
    return get_file_data_from_table(con, TABLE_NAME, filename, filepath)
