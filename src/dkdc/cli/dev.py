"""Development environment CLI with DuckLake and Postgres."""

import subprocess

import typer

from dkdc.cli.utils import (
    check_and_report_duckdb,
    ensure_postgres_with_feedback,
    operation_progress,
    print_error,
    print_header,
    print_info,
    print_key_value,
    print_success,
    spinner_task,
    stop_postgres_with_feedback,
)

dev_app = typer.Typer(name="dev", invoke_without_command=True, no_args_is_help=False)


def launch_sql_mode(metadata_schema: str):
    """Launch DuckDB CLI with Postgres catalog attached."""
    from dkdc.config.constants import DKDC_BANNER
    from dkdc.datalake.utils import get_multi_schema_sql_commands

    check_and_report_duckdb()

    sql_cmd = get_multi_schema_sql_commands(metadata_schema)

    print_header("dkdc dev (SQL)", "Connected with attachments to DuckLake databases")
    print_key_value("Default database", f"data_{metadata_schema}")

    # Print banner before entering DuckDB
    from dkdc.cli.utils import console

    console.print(DKDC_BANNER, style="primary")

    subprocess.run(["duckdb", "-cmd", sql_cmd], check=False)


def launch_python_mode(metadata_schema: str):
    """Launch IPython with Postgres catalog connection."""
    import ibis
    from IPython import start_ipython

    from dkdc.config import IBIS_INTERACTIVE, IBIS_MAX_COLUMNS, IBIS_MAX_ROWS
    from dkdc.config.constants import DKDC_BANNER
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

    print_header(
        "dkdc dev (Python)",
        "Connected with attachments to DuckLake databases (catalogs)",
    )
    print_key_value("Namespace", ", ".join(namespace.keys()))
    print_key_value("Default catalog", f"data_{metadata_schema}")

    # Print banner before entering IPython
    from dkdc.cli.utils import console

    console.print(DKDC_BANNER, style="primary")

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
):
    """Development environment CLI with DuckLake and Postgres."""
    from dkdc.config import DEFAULT_METADATA_SCHEMA

    # Set default schema if not provided
    if metadata_schema is None:
        metadata_schema = DEFAULT_METADATA_SCHEMA

    # Handle --down flag - stop postgres and exit
    if down:
        try:
            with spinner_task(
                "Stopping metadata database (Postgres)...",
                "Metadata database (Postgres) stopped",
            ):
                stop_postgres_with_feedback(quiet=True)
        except Exception as e:
            print_error("Failed to stop Postgres", str(e))
        raise typer.Exit(0)

    # Always ensure postgres is running
    try:
        from dkdc.cli.utils import check_and_report_docker

        with operation_progress(
            "Ensuring metadata database (Postgres) is running...",
            "Metadata database (Postgres) is ready",
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Checking Docker availability..."
            )
            check_and_report_docker()

            progress.update(
                progress.task_ids[0],
                description="Starting metadata database (Postgres)...",
            )
            ensure_postgres_with_feedback(quiet=True)

            progress.update(progress.task_ids[0], description="Finalizing setup...")

    except Exception as e:
        print_error("Setup failed", str(e))
        raise typer.Exit(1)

    # Handle --exit flag
    if exit_after_setup:
        print_success("Setup complete, exiting as requested")
        raise typer.Exit(0)

    mode = "SQL (DuckDB)" if sql else "Python (IPython)"
    print_info(f"Launching {mode} development environment")

    try:
        if sql:
            launch_sql_mode(metadata_schema)
        else:
            launch_python_mode(metadata_schema)
    except Exception as e:
        print_error("Failed to launch environment", str(e))
        raise typer.Exit(1)
