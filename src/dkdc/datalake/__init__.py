import os

import ibis

from dkdc.config import (
    DEFAULT_METADATA_SCHEMA,
    ENV_DEFAULT_METADATA_SCHEMA,
    IBIS_INTERACTIVE,
    IBIS_MAX_COLUMNS,
    IBIS_MAX_ROWS,
)

from . import secrets, utils

# Config
ibis.options.interactive = IBIS_INTERACTIVE
ibis.options.repr.interactive.max_rows = IBIS_MAX_ROWS
ibis.options.repr.interactive.max_columns = IBIS_MAX_COLUMNS

# Get default schema from environment variable
default_schema = os.getenv(ENV_DEFAULT_METADATA_SCHEMA, DEFAULT_METADATA_SCHEMA)

# Ensure postgres is running
utils.ensure_postgres_running()

# Create connection with all schemas attached
con = utils.get_duckdb_connection(default_schema=default_schema)

# Set ibis backend
ibis.set_backend(con)

# Exports
__all__ = ["ibis", "con", "secrets"]
