# Imports
import fnmatch
import io
import os
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import List, Union

import ibis
import ibis.expr.datatypes as dt

from dkdc.config import (
    BACKUP_FILENAME_TEMPLATE,
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
) -> str:
    """Add a file to the specified schema. Returns the filename."""
    ensure_files_table(con)

    file_path = Path(file_path).expanduser()
    path = str(file_path.parent)
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


def _load_gitignore_patterns(directory_path: Path) -> List[str]:
    """Load gitignore patterns from global and local gitignore files."""
    patterns = []

    # Load global gitignore
    global_gitignore = Path.home() / ".gitignore"
    if global_gitignore.exists():
        patterns.extend(global_gitignore.read_text().splitlines())

    # Load local gitignore files walking up the directory tree
    current_dir = directory_path
    while current_dir != current_dir.parent:
        gitignore_file = current_dir / ".gitignore"
        if gitignore_file.exists():
            patterns.extend(gitignore_file.read_text().splitlines())
        current_dir = current_dir.parent

    # Filter out empty lines and comments
    return [p.strip() for p in patterns if p.strip() and not p.strip().startswith("#")]


def _should_ignore(file_path: str, patterns: List[str]) -> bool:
    """Check if a file should be ignored based on gitignore patterns."""
    for pattern in patterns:
        if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(
            file_path, f"*/{pattern}"
        ):
            return True
    return False


def backup_directory(
    con: ibis.BaseBackend,
    directory_path: Union[str, Path],
) -> str:
    """Backup a directory as a zip file, respecting gitignore files. Returns the zip filename."""
    directory_path = Path(directory_path).expanduser()

    # Load gitignore patterns
    patterns = _load_gitignore_patterns(directory_path)

    # Create zip in memory
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        # Walk through directory and add all files
        for root, dirs, files in os.walk(directory_path):
            # Filter directories in place to skip ignored ones
            dirs[:] = [d for d in dirs if not _should_ignore(d, patterns)]

            for file in files:
                file_path = Path(root) / file
                # Create relative path for gitignore matching
                relative_path = file_path.relative_to(directory_path)

                # Skip if file matches gitignore patterns
                if not _should_ignore(str(relative_path), patterns):
                    zip_file.write(file_path, relative_path)

    # Get zip data as bytes
    zip_data = zip_buffer.getvalue()

    # Use directory name with .zip extension
    zip_filename = BACKUP_FILENAME_TEMPLATE.format(name=directory_path.name)
    path = str(directory_path.parent)

    return _add_file(con, path, zip_filename, zip_data)
