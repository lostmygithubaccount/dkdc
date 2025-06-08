"""Files management for the dkdc CLI."""

import os
import subprocess
import tempfile
from typing import Optional

import ibis
import typer

from dkdc.cli.utils import (
    operation_progress,
    print_error,
    print_header,
    print_key_value,
    print_success,
)

files_app = typer.Typer(name="files")


def get_file_from_datalake(con, filename: str) -> Optional[bytes]:
    """Retrieve the most recent version of a file from the datalake."""
    from dkdc.datalake.files import TABLE_NAME, ensure_files_table

    ensure_files_table(con)

    files_table = con.table(TABLE_NAME)
    result = (
        files_table.filter(
            (files_table["path"] == "./files") & (files_table["filename"] == filename)
        )
        .order_by(ibis.desc("updated_at"))
        .limit(1)
        .to_pyarrow()
        .to_pylist()
    )

    return result[0]["data"] if result else None


def save_file_to_datalake(con, filename: str, content: bytes) -> None:
    """Save a new version of a file to the datalake."""
    from dkdc.datalake.files import _add_file, ensure_files_table

    ensure_files_table(con)
    _add_file(con, "./files", filename, content)


def open_file(con, filename: str) -> None:
    """Open a file from the virtual files/ directory in your editor."""
    # Get editor from environment
    editor = os.environ.get("EDITOR", "vim")

    print_header("dkdc files", f"Opening {filename} in {editor}")
    print_key_value("Virtual path", f"./files/{filename}")

    try:
        with operation_progress(
            "Loading file from datalake...", "File editing completed"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )

            # Get file content from datalake
            progress.update(progress.task_ids[0], description=f"Loading {filename}...")
            content = get_file_from_datalake(con, filename)

            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode="w+b", suffix=f"_{filename}", delete=False
            ) as temp_file:
                temp_path = temp_file.name

                # Write existing content or create empty file
                if content:
                    temp_file.write(content)
                    print_key_value(
                        "Status", "Loaded existing file", value_style="success"
                    )
                else:
                    print_key_value(
                        "Status", "Creating new file", value_style="warning"
                    )

            progress.update(
                progress.task_ids[0], description=f"Opening {filename} in {editor}..."
            )

        # Open in editor (this will block until editor closes)
        result = subprocess.run([editor, temp_path], check=False)

        if result.returncode != 0:
            print_error("Editor failed", f"Editor exited with code {result.returncode}")
            raise typer.Exit(1)

        # Read the modified content
        with open(temp_path, "rb") as temp_file:
            new_content = temp_file.read()

        # Save back to datalake if content changed
        if new_content != (content or b""):
            with operation_progress(
                "Saving changes to datalake...", "Changes saved successfully"
            ):
                save_file_to_datalake(con, filename, new_content)
                print_key_value("Saved", f"./files/{filename}", value_style="success")
        else:
            print_success("No changes detected")

        # Clean up temporary file
        os.unlink(temp_path)

    except Exception as e:
        print_error("File operation failed", str(e))
        raise typer.Exit(1)


@files_app.command()
def list() -> None:
    """List all files in the virtual files/ directory."""
    from datetime import datetime

    from dkdc.datalake.files import TABLE_NAME, ensure_files_table
    from dkdc.datalake.utils import get_duckdb_connection

    try:
        with operation_progress(
            "Loading files from datalake...", "File list loaded"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()
            ensure_files_table(con)

            progress.update(progress.task_ids[0], description="Querying files...")

            files_table = con.table(TABLE_NAME)

            # Get the most recent version of each file
            result = (
                files_table.filter(files_table["path"] == "./files")
                .group_by("filename")
                .aggregate(updated_at=files_table["updated_at"].max())
                .order_by("updated_at")
                .to_pyarrow()
                .to_pylist()
            )

        print_header("dkdc files", "Virtual files directory")

        if not result:
            print_key_value("Status", "No files found", value_style="warning")
            return

        print_key_value("Files", f"{len(result)} found")
        print()

        for file_info in result:
            filename = file_info["filename"]
            updated_at = file_info["updated_at"]

            # Format timestamp
            if isinstance(updated_at, datetime):
                formatted_time = updated_at.strftime("%Y-%m-%d %H:%M")
            else:
                formatted_time = str(updated_at)

            print(f"- {filename} ({formatted_time})")

    except Exception as e:
        print_error("List operation failed", str(e))
        raise typer.Exit(1)


@files_app.command(name="open")
def open_cmd(
    filename: str = typer.Argument(
        help="Filename to open (e.g., 'work.md', 'life.md', 'pri.md', 'notes.md')"
    ),
) -> None:
    """Open a file from the virtual files/ directory in your editor."""
    from dkdc.datalake.utils import get_duckdb_connection

    con = get_duckdb_connection()
    open_file(con, filename)


@files_app.callback(invoke_without_command=True)
def files_main(
    ctx: typer.Context,
) -> None:
    """Manage files in the virtual files/ directory."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()
