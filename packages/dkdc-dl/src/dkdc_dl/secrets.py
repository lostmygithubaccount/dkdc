# Imports
from datetime import datetime

import ibis
import ibis.expr.datatypes as dt

from dkdc_dl.utils import DEFAULT_METADATA_SCHEMA

# Constants
TABLE_NAME = "secrets"
TABLE_SCHEMA = ibis.schema(
    {
        "key": str,
        "value": str,
        "description": str,
        "updated_at": dt.timestamp,
    }
)


# Functions
def ensure_secrets_table(
    con: ibis.BaseBackend, metadata_schema: str = DEFAULT_METADATA_SCHEMA
) -> None:
    """Ensure the secrets table exists in the specified schema."""
    # Check if table exists
    if TABLE_NAME not in con.list_tables():
        # Create the secrets table
        con.create_table(TABLE_NAME, schema=TABLE_SCHEMA)


def add_secret(
    con: ibis.BaseBackend,
    key: str,
    value: str,
    description: str = "",
) -> str:
    """Add a secret to the specified schema. Returns the secret ID."""
    ensure_secrets_table(con)

    now = datetime.now()
    data = {
        "key": [key],
        "value": [value],
        "description": [description],
        "updated_at": [now],
    }

    con.insert(TABLE_NAME, data)
    return value
