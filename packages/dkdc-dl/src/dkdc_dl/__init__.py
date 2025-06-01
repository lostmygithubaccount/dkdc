# Imports
import os
from pathlib import Path

import ibis

# Config
ibis.options.interactive = True
ibis.options.repr.interactive.max_rows = 40
ibis.options.repr.interactive.max_columns = None

# Determine catalog type from environment variable
catalog_type = os.getenv("DKDC_DL_CATALOG", "sqlite").lower()

# Ensure datalake directories exist
datalake_dir = Path("datalake")
sqlite_dir = datalake_dir / "sqlite"
postgres_dir = datalake_dir / "postgres"

sqlite_dir.mkdir(parents=True, exist_ok=True)
postgres_dir.mkdir(parents=True, exist_ok=True)

if catalog_type == "postgres":
    sql = """
INSTALL ducklake;
INSTALL postgres;

ATTACH 'ducklake:postgres:host=localhost port=5432 dbname=ducklake user=dkdc password=dkdc' AS dl
    (DATA_PATH 'datalake/postgres/');
USE dl;
""".strip()
else:  # default to sqlite
    sql = """
INSTALL ducklake;
INSTALL sqlite;

ATTACH 'ducklake:sqlite:dl.sqlite' AS dl
    (DATA_PATH 'datalake/sqlite/');
USE dl;
""".strip()

con = ibis.duckdb.connect()
con.raw_sql(sql)

ibis.set_backend(con)

# Exports
__all__ = ["ibis", "con"]
