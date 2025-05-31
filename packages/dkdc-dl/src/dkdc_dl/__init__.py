# Imports
import ibis

# Config
ibis.options.interactive = True
ibis.options.repr.interactive.max_rows = 40
ibis.options.repr.interactive.max_columns = None

sql = """
INSTALL ducklake;
INSTALL sqlite;

ATTACH 'ducklake:sqlite:dl.sqlite' AS dl
    (DATA_PATH 'datalake/');
USE dl;
""".strip()

con = ibis.duckdb.connect()
con.raw_sql(sql)

ibis.set_backend(con)

# Exports
__all__ = ["ibis", "con"]
