"""Files management for the dkdc CLI."""

import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

import ibis
import pyperclip
import typer
from watchfiles import watch

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
    from dkdc.datalake.files import get_file_data

    return get_file_data(con, filename)


def save_file_to_datalake(con, filename: str, content: bytes) -> None:
    """Save a new version of a file to the datalake."""
    from dkdc.datalake.files import _add_file, ensure_files_table

    ensure_files_table(con)
    _add_file(con, "./files", filename, content)


def open_file(con: ibis.BaseBackend, filename: str) -> None:
    """Open a file from the virtual files/ directory in your editor.

    Args:
        con: Database connection for the datalake
        filename: Name of the file to open/edit
    """
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

            # Create temporary file with same extension for proper syntax highlighting
            file_extension = Path(filename).suffix
            with tempfile.NamedTemporaryFile(
                mode="w+b",
                suffix=f"_{filename}" if not file_extension else file_extension,
                prefix=f"dkdc_{Path(filename).stem}_",
                delete=False,
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

        # Track the last saved content to avoid duplicate saves
        last_saved_content = content or b""
        save_lock = threading.Lock()
        auto_save_count = 0

        # Function to watch for file changes
        def watch_file_changes() -> None:
            """Monitor temporary file for changes and auto-save to datalake."""
            nonlocal last_saved_content, auto_save_count
            try:
                for changes in watch(temp_path):
                    # Read the current content
                    with open(temp_path, "rb") as f:
                        current_content = f.read()

                    # Only save if content actually changed
                    with save_lock:
                        if current_content != last_saved_content:
                            save_file_to_datalake(con, filename, current_content)
                            last_saved_content = current_content
                            auto_save_count += 1
                            # Don't print while editor is active - it interferes with terminal
            except Exception:
                # Watcher will stop when file is deleted or editor closes
                pass

        # Start file watcher in background thread
        watcher_thread = threading.Thread(target=watch_file_changes, daemon=True)
        watcher_thread.start()

        # Open in editor (this will block until editor closes)
        result = subprocess.run([editor, temp_path], check=False)

        if result.returncode != 0:
            print_error("Editor failed", f"Editor exited with code {result.returncode}")
            raise typer.Exit(1)

        # Give the watcher a moment to catch any last-second saves
        time.sleep(0.1)

        # Read the final content
        with open(temp_path, "rb") as temp_file:
            final_content = temp_file.read()

        # Save final changes if any (in case the last write wasn't caught)
        with save_lock:
            if final_content != last_saved_content:
                with operation_progress(
                    "Saving final changes to datalake...", "Changes saved successfully"
                ):
                    save_file_to_datalake(con, filename, final_content)
                    auto_save_count += 1

            # Report save statistics
            if auto_save_count > 0:
                if auto_save_count == 1:
                    print_key_value(
                        "Saved", f"./files/{filename} (1 time)", value_style="success"
                    )
                else:
                    print_key_value(
                        "Saved",
                        f"./files/{filename} ({auto_save_count} times)",
                        value_style="success",
                    )
            elif final_content == (content or b""):
                print_success("No changes detected")
            else:
                # Content changed but wasn't saved yet
                print_key_value("Saved", f"./files/{filename}", value_style="success")

        # Copy final content to clipboard as backup only if content changed from original
        if final_content != (content or b""):
            try:
                final_content_str = final_content.decode("utf-8")
                pyperclip.copy(final_content_str)
                print_key_value(
                    "Backup", "Content copied to clipboard", value_style="accent"
                )
            except Exception as e:
                print_key_value(
                    "Backup", f"Failed to copy to clipboard: {e}", value_style="warning"
                )

        # Clean up temporary file
        os.unlink(temp_path)

    except Exception as e:
        # Ensure temp file is cleaned up even on error
        if "temp_path" in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception:
                pass
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
                files_table.filter(files_table["filepath"] == "./files")
                .group_by("filename")
                .aggregate(fileupdated=files_table["fileupdated"].max())
                .order_by("fileupdated")
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
            fileupdated = file_info["fileupdated"]

            # Format timestamp
            if isinstance(fileupdated, datetime):
                formatted_time = fileupdated.strftime("%Y-%m-%d %H:%M")
            else:
                formatted_time = str(fileupdated)

            print(f"- {filename} ({formatted_time})")

    except Exception as e:
        print_error("List operation failed", str(e))
        raise typer.Exit(1)


@files_app.command()
def add(
    file_path: str = typer.Argument(help="Path to the file to add to the datalake"),
    filename: str = typer.Option(
        None,
        "--filename",
        help="Override the filename in the datalake (defaults to actual filename)",
    ),
    path: str = typer.Option(
        None,
        "--path",
        help="Virtual path in the datalake (defaults to './files')",
    ),
) -> None:
    """Add a file to the datalake."""
    from pathlib import Path

    from dkdc.datalake.files import add_file
    from dkdc.datalake.utils import get_duckdb_connection

    file_path_obj = Path(file_path).expanduser()

    if not file_path_obj.exists():
        print_error("File not found", f"'{file_path}' does not exist")
        raise typer.Exit(1)

    if not file_path_obj.is_file():
        print_error("Invalid target", f"'{file_path}' is not a file")
        raise typer.Exit(1)

    print_header("Add file", "Adding file to datalake")
    print_key_value("Source", file_path_obj)

    try:
        with operation_progress(
            "Adding file...", "File added successfully"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()

            progress.update(progress.task_ids[0], description="Adding file...")
            saved_filename = add_file(
                con, file_path_obj, filepath=path, filename=filename
            )

            progress.update(progress.task_ids[0], description="Finalizing...")

        print_key_value("Filename", saved_filename, value_style="success")
        print_key_value("Path", path or "./files", value_style="accent")

    except Exception as e:
        print_error("Add operation failed", str(e))
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


@files_app.command("dump")
def dump_files(
    path: str = typer.Argument(
        "temp/files",
        help="Directory path to dump files to (default: temp/files)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed progress",
    ),
) -> None:
    """Dump all files from the datalake to a local directory.

    Creates the directory if it doesn't exist and overwrites existing files.
    """
    from pathlib import Path

    from rich.console import Console

    from dkdc.datalake.files import TABLE_NAME, ensure_files_table
    from dkdc.datalake.utils import get_duckdb_connection

    console = Console()
    dump_path = Path(path).expanduser()

    try:
        with operation_progress(
            "📦 Dumping files from datalake...", "✓ Files dumped successfully"
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
                files_table.filter(files_table["filepath"] == "./files")
                .group_by("filename")
                .aggregate(
                    fileupdated=files_table["fileupdated"].max(),
                    filesize=files_table["filesize"].max(),
                )
                .order_by("filename")
                .to_pyarrow()
                .to_pylist()
            )

            if not result:
                console.print("\n[yellow]🔍 No files found in datalake[/yellow]\n")
                return

            # Create dump directory
            dump_path.mkdir(parents=True, exist_ok=True)

            progress.update(
                progress.task_ids[0],
                description=f"Dumping {len(result)} files to {dump_path}...",
            )

            # Dump each file
            dumped_count = 0
            total_size = 0

            for file_info in result:
                filename = file_info["filename"]

                # Get the actual file data
                file_data = get_file_from_datalake(con, filename)

                if file_data:
                    file_path = dump_path / filename
                    file_path.write_bytes(file_data)
                    dumped_count += 1
                    total_size += len(file_data)

                    if verbose:
                        console.print(f"  📄 {filename} ({len(file_data):,} bytes)")

        # Summary
        console.print(
            f"\n[green]✓[/green] Dumped [cyan]{dumped_count}[/cyan] files to [cyan]{dump_path}[/cyan]"
        )
        size_str = (
            f"{total_size:,} bytes"
            if total_size < 1024 * 1024
            else f"{total_size / 1024 / 1024:.1f} MB"
        )
        console.print(f"  Total size: [yellow]{size_str}[/yellow]\n")

    except Exception as e:
        print_error("Dump operation failed", str(e))
        raise typer.Exit(1)


@files_app.command("restore")
def restore_files(
    path: str = typer.Argument(
        help="Directory path to restore files from",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed progress",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files without confirmation",
    ),
) -> None:
    """Restore files from a local directory to the datalake.

    Adds each file in the directory to the datalake.
    """
    from pathlib import Path

    from rich.console import Console

    from dkdc.datalake.files import add_file
    from dkdc.datalake.utils import get_duckdb_connection

    console = Console()
    restore_path = Path(path).expanduser()

    if not restore_path.exists():
        console.print(f"\n[red]✗ Directory not found:[/red] {restore_path}\n")
        raise typer.Exit(1)

    if not restore_path.is_dir():
        console.print(f"\n[red]✗ Not a directory:[/red] {restore_path}\n")
        raise typer.Exit(1)

    try:
        # Get list of files to restore
        files_to_restore = [f for f in restore_path.iterdir() if f.is_file()]

        if not files_to_restore:
            console.print(f"\n[yellow]🔍 No files found in {restore_path}[/yellow]\n")
            return

        # Confirm restore
        if not force:
            console.print(
                f"\n[yellow]⚠️  Restore {len(files_to_restore)} files to datalake?[/yellow]"
            )
            from rich.prompt import Confirm

            if not Confirm.ask("   Continue?", default=True):
                console.print("\n[dim]Cancelled[/dim]\n")
                raise typer.Exit(0)

        with operation_progress(
            f"📥 Restoring {len(files_to_restore)} files...",
            "✓ Files restored successfully",
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()

            # Restore each file
            restored_count = 0
            total_size = 0
            errors = []

            for i, file_path in enumerate(files_to_restore):
                progress.update(
                    progress.task_ids[0],
                    description=f"Restoring {file_path.name}... ({i + 1}/{len(files_to_restore)})",
                )

                try:
                    saved_filename = add_file(con, file_path)
                    file_size = file_path.stat().st_size
                    restored_count += 1
                    total_size += file_size

                    if verbose:
                        console.print(f"  📄 {saved_filename} ({file_size:,} bytes)")

                except Exception as e:
                    errors.append((file_path.name, str(e)))
                    if verbose:
                        console.print(f"  [red]✗[/red] {file_path.name}: {e}")

        # Summary
        console.print(
            f"\n[green]✓[/green] Restored [cyan]{restored_count}[/cyan] files to datalake"
        )
        size_str = (
            f"{total_size:,} bytes"
            if total_size < 1024 * 1024
            else f"{total_size / 1024 / 1024:.1f} MB"
        )
        console.print(f"  Total size: [yellow]{size_str}[/yellow]")

        if errors:
            console.print(f"\n[red]⚠️  {len(errors)} files failed:[/red]")
            for filename, error in errors[:5]:  # Show first 5 errors
                console.print(f"  - {filename}: {error}")
            if len(errors) > 5:
                console.print(f"  ... and {len(errors) - 5} more")

        console.print()

    except Exception as e:
        if "Cancelled" not in str(e):
            print_error("Restore operation failed", str(e))
        raise typer.Exit(1)


@files_app.callback(invoke_without_command=True)
def files_main(
    ctx: typer.Context,
) -> None:
    """Manage files in the virtual files/ directory."""
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()
