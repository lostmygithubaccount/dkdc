"""Backup functionality for the dkdc CLI."""

from pathlib import Path

import typer

from dkdc.cli.utils import (
    operation_progress,
    print_error,
    print_header,
    print_key_value,
)

backup_app = typer.Typer(
    name="backup", invoke_without_command=True, no_args_is_help=False
)


@backup_app.callback()
def backup_default(
    directory: str = typer.Argument(
        ".",
        help="Directory to backup (defaults to current directory)",
    ),
) -> None:
    """Backup a directory to the datalake."""
    directory_path = Path(directory).resolve()

    if not directory_path.exists():
        print_error("Directory not found", f"'{directory_path}' does not exist")
        raise typer.Exit(1)

    if not directory_path.is_dir():
        print_error("Invalid target", f"'{directory_path}' is not a directory")
        raise typer.Exit(1)

    print_header("Backup directory", "Creating backup in datalake")
    print_key_value("Source", directory_path)

    try:
        with operation_progress(
            "Creating backup archive...", "Backup completed successfully"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Initializing backup process..."
            )

            from dkdc.datalake.files import backup_directory
            from dkdc.datalake.utils import get_duckdb_connection

            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()

            progress.update(
                progress.task_ids[0], description="Creating backup archive..."
            )
            zip_filename = backup_directory(con, directory_path)

            progress.update(progress.task_ids[0], description="Finalizing backup...")

        print_key_value("Archive", zip_filename, value_style="success")

    except Exception as e:
        print_error("Backup failed", str(e))
        raise typer.Exit(1)
