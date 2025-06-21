# Imports
from typing import Optional

import ibis

from dkdc.config import SECRETS_TABLE_NAME
from dkdc.datalake.files import (
    FILE_TABLE_SCHEMA,
    _add_file_to_table,
    ensure_file_table,
)

# Constants
TABLE_NAME = SECRETS_TABLE_NAME
TABLE_SCHEMA = FILE_TABLE_SCHEMA


# Functions
def ensure_secrets_table(con: ibis.BaseBackend) -> None:
    """Ensure the secrets table exists."""
    ensure_file_table(con, TABLE_NAME)


def add_secret(
    con: ibis.BaseBackend,
    secretkey: str,
    secretvalue: str,
    secretdescription: str = "",
    filepath: Optional[str] = None,
) -> str:
    """Add a secret to the specified schema. Returns the secret key.

    Secrets are stored as files with:
    - filepath: Virtual path (default: "./secrets")
    - filename: The secret key
    - filedata: The secret value encoded as bytes
    - filesize: Size of the encoded secret value
    - fileupdated: Timestamp when the secret was added/updated

    The secretdescription is currently not stored but could be added
    as metadata in the filepath or filename.
    """
    # Use provided filepath or default to "./secrets"
    if filepath is None:
        filepath = "./secrets"

    # Store secret value as bytes
    filedata = secretvalue.encode("utf-8")

    # Use secret key as filename
    _add_file_to_table(con, TABLE_NAME, filepath, secretkey, filedata)
    return secretkey


# Secret Retrieval Functions
def get_secret(
    con: ibis.BaseBackend,
    secretkey: str,
    filepath: Optional[str] = None,
) -> Optional[str]:
    """Retrieve a secret value from the secrets table.

    Args:
        con: Database connection
        secretkey: The secret key (stored as filename)
        filepath: Optional filepath filter. If None, uses "./secrets".

    Returns:
        Secret value as string or None if not found
    """
    from dkdc.datalake.files import get_file_data_from_table

    # Default filepath for secrets
    if filepath is None:
        filepath = "./secrets"

    data = get_file_data_from_table(con, TABLE_NAME, secretkey, filepath)
    return data.decode("utf-8") if data else None
