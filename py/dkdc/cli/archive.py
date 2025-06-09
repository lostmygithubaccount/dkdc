"""Archive functionality for the dkdc CLI."""

from pathlib import Path

import typer

from dkdc.cli.utils import (
    operation_progress,
    print_error,
    print_header,
    print_key_value,
)

archive_app = typer.Typer(
    name="archive", invoke_without_command=True, no_args_is_help=False
)


@archive_app.callback()
def archive_default(
    directory: str = typer.Argument(
        ".",
        help="Directory to archive (defaults to current directory)",
    ),
    path: str = typer.Option(
        None,
        "--path",
        help="Override the archive path in the datalake",
    ),
    filename: str = typer.Option(
        None,
        "--filename",
        help="Override the archive filename",
    ),
) -> None:
    """Archive a directory to the datalake."""
    directory_path = Path(directory).resolve()

    if not directory_path.exists():
        print_error("Directory not found", f"'{directory_path}' does not exist")
        raise typer.Exit(1)

    if not directory_path.is_dir():
        print_error("Invalid target", f"'{directory_path}' is not a directory")
        raise typer.Exit(1)

    print_header("Archive directory", "Creating archive in datalake")
    print_key_value("Source", directory_path)

    try:
        with operation_progress(
            "Creating archive...", "Archive completed successfully"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Initializing archive process..."
            )

            from dkdc.datalake.archives import archive_directory
            from dkdc.datalake.utils import get_duckdb_connection

            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()

            progress.update(progress.task_ids[0], description="Creating archive...")
            zip_filename = archive_directory(
                con, directory_path, archive_path=path, archive_filename=filename
            )

            progress.update(progress.task_ids[0], description="Finalizing archive...")

        print_key_value("Archive", zip_filename, value_style="success")
        if path:
            print_key_value("Path", path, value_style="accent")
        if filename:
            print_key_value("Filename", filename, value_style="accent")

    except Exception as e:
        print_error("Archive failed", str(e))
        raise typer.Exit(1)
