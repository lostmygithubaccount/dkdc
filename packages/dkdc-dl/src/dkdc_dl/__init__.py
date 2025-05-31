# Imports
import os

import ibis

# Config
ibis.options.interactive = True
ibis.options.repr.interactive.max_rows = 40
ibis.options.repr.interactive.max_columns = None

# Determine catalog type from environment variable
catalog_type = os.getenv("DKDC_DL_CATALOG", "sqlite").lower()

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
