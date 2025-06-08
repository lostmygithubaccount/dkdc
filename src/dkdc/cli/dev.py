"""Development environment CLI with DuckLake and Postgres."""

import subprocess

import typer
from rich.console import Console

console = Console()
dev_app = typer.Typer(name="dev", invoke_without_command=True, no_args_is_help=False)


def launch_sql_mode(metadata_schema: str):
    """Launch DuckDB CLI with Postgres catalog attached."""
    from dkdc.datalake.utils import check_duckdb, get_multi_schema_sql_commands

    check_duckdb()

    sql_cmd = get_multi_schema_sql_commands(metadata_schema)

    console.print("📦 Available: dl catalog, ducklake extension")
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")
    console.print("🔗 Connected to all schemas: dev, stage, prod")
    console.print(f"📋 Default schema: data_{metadata_schema}")

    subprocess.run(["duckdb", "-cmd", sql_cmd], check=False)


def launch_python_mode(metadata_schema: str):
    """Launch IPython with Postgres catalog connection."""
    import ibis
    from IPython import start_ipython

    from dkdc.config import IBIS_INTERACTIVE, IBIS_MAX_COLUMNS, IBIS_MAX_ROWS
    from dkdc.datalake import files, secrets
    from dkdc.datalake.utils import get_duckdb_connection, get_postgres_connection

    # Get multi-schema connection
    con = get_duckdb_connection(default_schema=metadata_schema)

    # Get catalog connection for direct catalog access
    metacon = get_postgres_connection(metadata_schema=metadata_schema)

    # Configure ibis
    ibis.options.interactive = IBIS_INTERACTIVE
    ibis.options.repr.interactive.max_rows = IBIS_MAX_ROWS
    ibis.options.repr.interactive.max_columns = IBIS_MAX_COLUMNS
    ibis.set_backend(con)

    # Prepare namespace
    namespace = {
        # Must-have top-level imports
        "ibis": ibis,
        # Data connections
        "con": con,
        "metacon": metacon,
        # dkdc submodules
        "utils": ibis.util,
        "files": files,
        "secrets": secrets,
    }

    console.print(f"📦 Available: {', '.join(namespace.keys())}")
    console.print(f"🏷️ METADATA_SCHEMA={metadata_schema}")
    console.print("🔗 Connected to all schemas: dev, stage, prod")
    console.print(f"📋 Default schema: data_{metadata_schema}")

    # Start IPython with our namespace
    start_ipython(argv=["--no-banner"], user_ns=namespace)


@dev_app.callback()
def dev_main(
    sql: bool = typer.Option(
        False, "--sql", help="Enter DuckDB CLI instead of IPython"
    ),
    down: bool = typer.Option(
        False, "--down", help="Stop and remove the Postgres container"
    ),
    metadata_schema: str = typer.Option(
        None,
        "--metadata-schema",
        "-s",
        help="Metadata schema to use",
    ),
    exit_after_setup: bool = typer.Option(
        False, "--exit", help="Exit after setup without starting REPL"
    ),
    backup_metadata_flag: bool = typer.Option(
        False,
        "--backup-metadata",
        help="Create metadata backup as metadata_backup.sql and exit",
    ),
):
    """Development environment CLI with DuckLake and Postgres."""
    from dkdc.config import DEFAULT_METADATA_SCHEMA

    # Set default schema if not provided
    if metadata_schema is None:
        metadata_schema = DEFAULT_METADATA_SCHEMA

    # Handle --down flag - stop postgres and exit
    if down:
        from dkdc.datalake.utils import stop_postgres

        try:
            stop_postgres()
        except Exception:
            pass
        raise typer.Exit(0)

    # Handle --backup-metadata flag - create backup and exit
    if backup_metadata_flag:
        from dkdc.datalake.utils import backup_metadata

        try:
            backup_metadata()
        except Exception as e:
            console.print(f"❌ Backup failed: {e}")
            raise typer.Exit(1)
        raise typer.Exit(0)

    # Always ensure postgres is running
    try:
        from dkdc.datalake.utils import check_docker, ensure_postgres_running

        check_docker()
        ensure_postgres_running()
    except Exception as e:
        console.print(f"❌ Setup failed: {e}")
        raise typer.Exit(1)

    # Handle --exit flag
    if exit_after_setup:
        console.print("✅ Setup complete, exiting as requested")
        raise typer.Exit(0)

    mode_emoji = "🦆" if sql else "🐍"
    console.print(f"dev: {mode_emoji} (language) 🐘 (postgres)")

    try:
        if sql:
            launch_sql_mode(metadata_schema)
        else:
            launch_python_mode(metadata_schema)
    except Exception as e:
        console.print(f"❌ Failed to launch: {e}")
        raise typer.Exit(1)
