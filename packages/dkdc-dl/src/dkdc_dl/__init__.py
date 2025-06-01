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
data_path = f"datalake/catalog-{catalog_type}/"

# Ensure datalake directories exist
Path(data_path).mkdir(parents=True, exist_ok=True)

if catalog_type == "postgres":
    sql = f"""
INSTALL ducklake;
INSTALL postgres;

ATTACH 'ducklake:postgres:host=localhost port=5432 dbname=ducklake user=dkdc password=dkdc' AS dl
    (DATA_PATH '{data_path}');
USE dl;
""".strip()
else:  # default to sqlite
    sql = f"""
INSTALL ducklake;
INSTALL sqlite;

ATTACH 'ducklake:sqlite:dl.sqlite' AS dl
    (DATA_PATH '{data_path}');
USE dl;
""".strip()

con = ibis.duckdb.connect()
con.raw_sql(sql)

ibis.set_backend(con)

# Exports
__all__ = ["ibis", "con"]
