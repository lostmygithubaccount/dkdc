#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "dkdc",
#     "duckdb",
#     "ipython",
#     "rich",
#     "typer",
# ]
#
# [tool.uv.sources]
# dkdc = { path = ".", editable = true }
# ///

import os
import subprocess
import sys

import typer
from rich.console import Console

console = Console()
app = typer.Typer()


@app.command()
def main(
    sql: bool = typer.Option(
        False, "--sql", help="Enter DuckDB CLI instead of IPython"
    ),
    catalog: str = typer.Option(
        "sqlite", "--catalog", help="Catalog type: sqlite or postgres"
    ),
):
    """DKDC development environment CLI."""

    os.environ["DKDC_DL_CATALOG"] = catalog.lower()

    catalog_emoji = "🐘" if catalog.lower() == "postgres" else "🗂️"
    mode_emoji = "🦆" if sql else "🐍"
    console.print(f"dkdc dev: {mode_emoji} (language) {catalog_emoji} (catalog)")

    if sql:
        # SQL commands for catalog setup
        if catalog.lower() == "postgres":
            sql_cmd = "INSTALL ducklake; INSTALL postgres; ATTACH 'ducklake:postgres:host=localhost port=5432 dbname=ducklake user=dkdc password=dkdc' AS dl (DATA_PATH 'datalake/postgres/'); USE dl;"
        else:
            sql_cmd = "INSTALL ducklake; INSTALL sqlite; ATTACH 'ducklake:sqlite:dl.sqlite' AS dl (DATA_PATH 'datalake/sqlite/'); USE dl;"

        subprocess.run(["duckdb", "-cmd", sql_cmd], check=False)
    else:
        # IPython startup code with variable display
        startup = f"""
import os
os.environ['DKDC_DL_CATALOG']='{catalog.lower()}'
from dkdc_dl import con, ibis
import dkdc
try:
    import dkdc_sh
except ImportError:
    dkdc_sh = None

bucket = 'gs://ascend-io-gcs-public'
feedback_ascenders_glob = 'ottos-expeditions/lakev0/generated/events/feedback_ascenders.parquet/year=*/month=*/day=*/*.parquet'

print('📦 Available: con, ibis, dkdc' + (', dkdc_sh' if dkdc_sh else '') + ', bucket, feedback_ascenders_glob')
print('🌍 DKDC_DL_CATALOG=' + os.environ.get('DKDC_DL_CATALOG', 'unset'))
"""

        subprocess.run(
            [sys.executable, "-m", "IPython", "-c", startup, "-i", "--no-banner"],
            check=False,
        )


if __name__ == "__main__":
    app()
