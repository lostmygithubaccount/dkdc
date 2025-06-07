import os

import ibis

from . import secrets, utils

# Config
ibis.options.interactive = True
ibis.options.repr.interactive.max_rows = 40
ibis.options.repr.interactive.max_columns = None

# Get default schema from environment variable
default_schema = os.getenv(
    "DKDC_DL_DEFAULT_METADATA_SCHEMA", utils.DEFAULT_METADATA_SCHEMA
)

# Ensure postgres is running
utils.ensure_postgres_running()

# Create connection with all schemas attached
con = utils.get_multi_schema_connection(default_schema=default_schema)

# Set ibis backend
ibis.set_backend(con)

# Exports
__all__ = ["ibis", "con", "secrets"]
