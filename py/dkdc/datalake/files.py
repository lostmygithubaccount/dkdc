# Imports
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Union

import ibis
import ibis.expr.datatypes as dt

from dkdc.config import (
    DEFAULT_METADATA_SCHEMA,
    FILES_TABLE_NAME,
)

# Constants
TABLE_NAME = FILES_TABLE_NAME
TABLE_SCHEMA = ibis.schema(
    {
        "path": str,
        "filename": str,
        "data": dt.binary,
        "size": int,
        "updated_at": dt.timestamp,
    }
)


# Functions
def ensure_files_table(
    con: ibis.BaseBackend, metadata_schema: str = DEFAULT_METADATA_SCHEMA
) -> None:
    """Ensure the files table exists in the specified schema."""
    # Check if table exists
    if TABLE_NAME not in con.list_tables():
        # Create the files table
        con.create_table(TABLE_NAME, schema=TABLE_SCHEMA)


def add_file(
    con: ibis.BaseBackend,
    file_path: Union[str, Path],
    path: Optional[str] = None,
    filename: Optional[str] = None,
) -> str:
    """Add a file to the specified schema. Returns the filename.

    Args:
        con: Database connection
        file_path: Path to the file to add
        path: Optional virtual path in the datalake. If None, uses "./files".
        filename: Optional custom filename. If None, uses the actual filename.
    """
    ensure_files_table(con)

    file_path = Path(file_path).expanduser()

    # Use provided path or default to "./files"
    if path is None:
        path = "./files"

    # Use provided filename or actual filename
    if filename is None:
        filename = file_path.name

    data = file_path.read_bytes()

    return _add_file(con, path, filename, data)


def _add_file(
    con: ibis.BaseBackend,
    path: str,
    filename: str,
    data: bytes,
) -> str:
    """Internal function to add file data directly. Returns the filename."""
    ensure_files_table(con)

    now = datetime.now(UTC)
    file_data = {
        "path": [path],
        "filename": [filename],
        "data": [data],
        "size": [len(data)],
        "updated_at": [now],
    }

    con.insert(TABLE_NAME, file_data)
    return filename
