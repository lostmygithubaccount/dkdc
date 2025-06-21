"""Development management."""

import subprocess

import typer

from dkdc.cli.utils import (
    check_and_report_duckdb,
    ensure_setup_with_feedback,
    operation_progress,
    print_error,
    print_header,
    print_info,
    print_key_value,
    print_success,
)

dev_app = typer.Typer(name="dev", invoke_without_command=True, no_args_is_help=False)


def launch_sql_mode():
    """Launch DuckDB CLI with DuckLake attached."""
    from dkdc.config.constants import DKDC_BANNER
    from dkdc.datalake.utils import get_sql_commands

    check_and_report_duckdb()

    sql_cmd = get_sql_commands()

    print_header("dkdc dev (SQL)", "Connected to DuckLake database")
    print_key_value("Database", "my_ducklake")

    # Print banner before entering DuckDB
    from dkdc.cli.utils import console

    console.print(DKDC_BANNER, style="primary")

    subprocess.run(["duckdb", "-cmd", sql_cmd], check=False)


def launch_python_mode():
    """Launch IPython with DuckDB connection."""
    import ibis
    from IPython import start_ipython

    from dkdc.config import IBIS_INTERACTIVE, IBIS_MAX_COLUMNS, IBIS_MAX_ROWS
    from dkdc.config.constants import DKDC_BANNER
    from dkdc.datalake import files, secrets
    from dkdc.datalake.utils import (
        get_duckdb_connection,
        get_metadata_connection,
    )

    # Get DuckDB connection with DuckLake attached
    con = get_duckdb_connection()

    # Get metadata connection for direct metadata access
    metacon = get_metadata_connection()

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
        "files": files,
        "secrets": secrets,
    }

    print_header(
        "dkdc dev (Python)",
        "Connected to DuckLake database",
    )
    print_key_value("Namespace", ", ".join(namespace.keys()))
    print_key_value("Database", "my_ducklake")

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
    exit_after_setup: bool = typer.Option(
        False, "--exit", help="Exit after setup without starting REPL"
    ),
):
    """Enter a development REPL (IPython or DuckDB)."""

    # Ensure database setup
    try:
        with operation_progress(
            "Setting up database...",
            "Database is ready",
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Checking DuckDB availability..."
            )
            check_and_report_duckdb()

            progress.update(
                progress.task_ids[0],
                description="Setting up database...",
            )
            ensure_setup_with_feedback(quiet=True)

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
            launch_sql_mode()
        else:
            launch_python_mode()
    except Exception as e:
        print_error("Failed to launch environment", str(e))
        raise typer.Exit(1)
