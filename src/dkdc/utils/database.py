# imports
import ibis

from dkdc.defaults import DATABASE_PATH

# table names
TABLES = {
    "dkdc": "dkdc",
}


# functions
def connect(url: str = DATABASE_PATH) -> ibis.BaseBackend:
    """
    Connect to a database.
    """
    if url.endswith(".ddb"):
        return ibis.duckdb.connect(url)
    else:
        raise NotImplementedError("Only DuckDB databases are supported.")
