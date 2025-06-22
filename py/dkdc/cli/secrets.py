"""Secrets management for the dkdc CLI."""

import getpass
from typing import Optional

import pyperclip
import typer

from dkdc.cli.utils import (
    operation_progress,
    print_error,
    print_header,
    print_key_value,
    print_success,
)

secrets_app = typer.Typer(name="secrets")


@secrets_app.command("list")
def list_secrets(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed information including sizes and paths",
    ),
) -> None:
    """List all secrets in the datalake."""
    from datetime import datetime

    from rich.console import Console
    from rich.table import Table

    from dkdc.datalake.secrets import TABLE_NAME, ensure_secrets_table
    from dkdc.datalake.utils import get_duckdb_connection

    console = Console()

    try:
        with operation_progress(
            "🔐 Loading secrets...", "✓ Secrets loaded"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()
            ensure_secrets_table(con)

            progress.update(progress.task_ids[0], description="Querying secrets...")

            secrets_table = con.table(TABLE_NAME)

            # Get the most recent version of each secret with size info
            if verbose:
                result = (
                    secrets_table.filter(secrets_table["filepath"] == "./secrets")
                    .group_by("filename")
                    .aggregate(
                        fileupdated=secrets_table["fileupdated"].max(),
                        filesize=secrets_table["filesize"].max(),
                    )
                    .order_by("filename")
                    .to_pyarrow()
                    .to_pylist()
                )
            else:
                result = (
                    secrets_table.filter(secrets_table["filepath"] == "./secrets")
                    .group_by("filename")
                    .aggregate(fileupdated=secrets_table["fileupdated"].max())
                    .order_by("filename")
                    .to_pyarrow()
                    .to_pylist()
                )

        if not result:
            console.print("\n[yellow]🔍 No secrets found[/yellow]\n")
            return

        # Create a nice table
        table = Table(title=f"\n🔐 Secrets ({len(result)} total)")
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Updated", style="green")
        if verbose:
            table.add_column("Size", style="yellow")
            table.add_column("Path", style="dim")

        for secret_info in result:
            secretkey = secret_info["filename"]
            fileupdated = secret_info["fileupdated"]

            # Format timestamp as relative time
            if isinstance(fileupdated, datetime):
                now = datetime.now(fileupdated.tzinfo or datetime.now().tzinfo)
                delta = now - fileupdated
                if delta.days > 7:
                    formatted_time = fileupdated.strftime("%Y-%m-%d")
                elif delta.days > 0:
                    formatted_time = f"{delta.days}d ago"
                elif delta.seconds > 3600:
                    formatted_time = f"{delta.seconds // 3600}h ago"
                elif delta.seconds > 60:
                    formatted_time = f"{delta.seconds // 60}m ago"
                else:
                    formatted_time = "just now"
            else:
                formatted_time = str(fileupdated)

            if verbose:
                filesize = secret_info.get("filesize", 0)
                size_str = (
                    f"{filesize} bytes"
                    if filesize < 1024
                    else f"{filesize / 1024:.1f} KB"
                )
                table.add_row(secretkey, formatted_time, size_str, "./secrets")
            else:
                table.add_row(secretkey, formatted_time)

        console.print(table)
        console.print()

    except Exception as e:
        print_error("List operation failed", str(e))
        raise typer.Exit(1)


@secrets_app.command("get")
def get_secret(
    key: str = typer.Argument(help="Secret key to retrieve"),
    clipboard: bool = typer.Option(
        False,
        "--clipboard",
        "-c",
        help="Copy secret value to clipboard instead of displaying",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed output with metadata",
    ),
    export: bool = typer.Option(
        False,
        "--export",
        "-e",
        help="Output in shell export format",
    ),
) -> None:
    """Get a secret value from the datalake.

    By default, outputs only the secret value for easy piping.
    Use --verbose for detailed output.
    """
    import sys

    from dkdc.datalake.secrets import get_secret as get_secret_value
    from dkdc.datalake.utils import get_duckdb_connection

    try:
        # Only show progress in verbose mode
        if verbose:
            with operation_progress(
                f"🔐 Retrieving secret '{key}'...", "✓ Secret retrieved"
            ) as progress:
                progress.update(
                    progress.task_ids[0], description="Connecting to datalake..."
                )
                con = get_duckdb_connection()

                progress.update(
                    progress.task_ids[0], description=f"Looking up secret '{key}'..."
                )
                value = get_secret_value(con, key)
        else:
            # Silent retrieval for piping
            con = get_duckdb_connection()
            value = get_secret_value(con, key)

        if value is None:
            if verbose:
                print_error("Secret not found", f"No secret with key '{key}' exists")
            else:
                # For piping, output to stderr
                print(f"Error: Secret '{key}' not found", file=sys.stderr)
            raise typer.Exit(1)

        if clipboard:
            try:
                pyperclip.copy(value)
                if verbose:
                    print_success(f"🔐 Secret '{key}' copied to clipboard")
                else:
                    # Minimal output to stderr so stdout stays clean
                    print("Copied to clipboard", file=sys.stderr)
            except Exception as e:
                if verbose:
                    print_error("Clipboard error", f"Failed to copy to clipboard: {e}")
                else:
                    print(f"Error: Failed to copy to clipboard: {e}", file=sys.stderr)
                # Still output the value
                if export:
                    print(f"export {key}='{value}'")
                else:
                    print(value)
        elif export:
            # Shell export format
            print(f"export {key}='{value}'")
        elif verbose:
            # Detailed output
            print_header("🔐 Secret retrieved", key)
            print_key_value("Key", key, value_style="cyan")
            print_key_value("Value", value, value_style="green")
            print_key_value("Length", f"{len(value)} characters", value_style="yellow")
        else:
            # Default: just output the value for piping
            print(value)

    except Exception as e:
        if "not found" not in str(e).lower():
            if verbose:
                print_error("Get operation failed", str(e))
            else:
                print(f"Error: {e}", file=sys.stderr)
        raise typer.Exit(1)


@secrets_app.command("set")
def set_secret(
    key: str = typer.Argument(help="Secret key"),
    value: Optional[str] = typer.Argument(
        None, help="Secret value (if not provided, will prompt securely)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing secret without confirmation",
    ),
    description: str = typer.Option(
        "",
        "--description",
        "-d",
        help="Optional description for the secret",
    ),
    from_stdin: bool = typer.Option(
        False,
        "--stdin",
        help="Read secret value from stdin",
    ),
) -> None:
    """Set a secret in the datalake.

    Examples:
        dkdc secrets set API_KEY my-secret-value
        dkdc secrets set API_KEY  # Will prompt for value
        echo "my-secret" | dkdc secrets set API_KEY --stdin
    """
    import sys

    from rich.console import Console

    from dkdc.datalake.secrets import add_secret
    from dkdc.datalake.secrets import get_secret as get_existing_secret
    from dkdc.datalake.utils import get_duckdb_connection

    console = Console()

    try:
        # Read from stdin if requested
        if from_stdin:
            if value is not None:
                print_error("Conflict", "Cannot specify both value and --stdin")
                raise typer.Exit(1)
            value = sys.stdin.read().strip()
            if not value:
                print_error("Empty input", "No data received from stdin")
                raise typer.Exit(1)

        # If no value provided, prompt securely
        elif value is None:
            console.print(f"\n🔐 [bold cyan]Setting secret:[/bold cyan] {key}\n")
            value = getpass.getpass("📝 Enter value: ")

            # Confirm the value
            confirm = getpass.getpass("✓  Confirm value: ")
            if value != confirm:
                console.print("\n[red]✗ Values don't match[/red]\n")
                raise typer.Exit(1)

        if not value:
            print_error("Empty value", "Secret value cannot be empty")
            raise typer.Exit(1)

        with operation_progress(
            f"🔐 Saving secret '{key}'...", f"✓ Secret '{key}' saved"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()

            # Check if secret already exists
            progress.update(
                progress.task_ids[0], description="Checking existing secrets..."
            )
            existing = get_existing_secret(con, key)

            if existing and not force:
                console.print(f"\n[yellow]⚠️  Secret '{key}' already exists[/yellow]")
                console.print("   Use --force to overwrite\n")
                raise typer.Exit(1)

            # Save the secret
            progress.update(
                progress.task_ids[0], description="Encrypting and saving..."
            )
            add_secret(con, key, value, description)

        # Success output
        console.print(
            f"\n[green]✓[/green] Secret [cyan]{key}[/cyan] {'updated' if existing else 'created'}"
        )
        if description:
            console.print(f"  [dim]Description: {description}[/dim]")
        console.print(f"  [dim]Length: {len(value)} characters[/dim]\n")

    except Exception as e:
        if (
            "already exists" not in str(e).lower()
            and "don't match" not in str(e).lower()
        ):
            print_error("Set operation failed", str(e))
        raise typer.Exit(1)


@secrets_app.command("delete")
def delete_secret(
    key: str = typer.Argument(help="Secret key to delete"),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Delete without confirmation",
    ),
) -> None:
    """Delete a secret from the datalake."""
    from rich.console import Console
    from rich.prompt import Confirm

    from dkdc.datalake.secrets import TABLE_NAME, ensure_secrets_table, get_secret
    from dkdc.datalake.utils import get_duckdb_connection

    console = Console()

    try:
        with operation_progress(
            f"🔍 Checking secret '{key}'...", "✓ Deletion completed"
        ) as progress:
            progress.update(
                progress.task_ids[0], description="Connecting to datalake..."
            )
            con = get_duckdb_connection()
            ensure_secrets_table(con)

            # Check if secret exists
            progress.update(
                progress.task_ids[0], description=f"Looking up secret '{key}'..."
            )
            existing = get_secret(con, key)

            if not existing:
                console.print(f"\n[red]✗ Secret '{key}' not found[/red]\n")
                raise typer.Exit(1)

        # Confirm deletion
        if not force:
            console.print(f"\n[yellow]⚠️  Delete secret '{key}'?[/yellow]")
            if not Confirm.ask("   Are you sure?", default=False):
                console.print("\n[dim]Cancelled[/dim]\n")
                raise typer.Exit(0)

        with operation_progress(
            f"🗑️  Deleting secret '{key}'...", f"✓ Secret '{key}' deleted"
        ):
            # Since we're using a file-based system, we need to mark it as deleted
            # or filter it out. For now, we'll add a deleted marker by updating
            # the filepath to "./secrets/.deleted"
            from datetime import UTC, datetime

            from dkdc.datalake.files import _add_file_to_table

            # Add a deletion marker
            deletion_marker = f"Deleted at {datetime.now(UTC).isoformat()}"
            _add_file_to_table(
                con,
                TABLE_NAME,
                "./secrets/.deleted",
                key,
                deletion_marker.encode("utf-8"),
            )

        console.print(f"\n[green]✓[/green] Secret [cyan]{key}[/cyan] deleted\n")

    except Exception as e:
        if "not found" not in str(e).lower() and "cancelled" not in str(e).lower():
            print_error("Delete operation failed", str(e))
        raise typer.Exit(1)


@secrets_app.command("export")
def export_secrets(
    prefix: str = typer.Option(
        None,
        "--prefix",
        "-p",
        help="Only export secrets with this prefix",
    ),
    format: str = typer.Option(
        "shell",
        "--format",
        "-f",
        help="Export format: shell, dotenv, json",
    ),
) -> None:
    """Export all secrets in various formats.

    Examples:
        dkdc secrets export                    # Shell export format
        dkdc secrets export -f dotenv > .env   # Create .env file
        dkdc secrets export -f json            # JSON format
        dkdc secrets export -p API_            # Only API_ prefixed secrets
    """
    import json
    import sys

    from dkdc.datalake.secrets import TABLE_NAME, ensure_secrets_table, get_secret
    from dkdc.datalake.utils import get_duckdb_connection

    try:
        con = get_duckdb_connection()
        ensure_secrets_table(con)

        secrets_table = con.table(TABLE_NAME)

        # Get all current secrets
        query = secrets_table.filter(secrets_table["filepath"] == "./secrets")

        if prefix:
            query = query.filter(secrets_table["filename"].contains(prefix))

        result = (
            query.group_by("filename")
            .aggregate(fileupdated=secrets_table["fileupdated"].max())
            .order_by("filename")
            .to_pyarrow()
            .to_pylist()
        )

        if not result:
            print(
                f"# No secrets found{' with prefix ' + prefix if prefix else ''}",
                file=sys.stderr,
            )
            raise typer.Exit(0)

        # Collect all secrets and their values
        secrets = {}
        for secret_info in result:
            key = secret_info["filename"]
            value = get_secret(con, key)
            if value:
                secrets[key] = value

        # Output in requested format
        if format == "shell":
            print("# dkdc secrets export")
            for key, value in secrets.items():
                # Escape single quotes in value
                escaped_value = value.replace("'", "'\"'\"'")
                print(f"export {key}='{escaped_value}'")
        elif format == "dotenv":
            print("# dkdc secrets export")
            for key, value in secrets.items():
                # Escape newlines and quotes for dotenv
                escaped_value = value.replace('"', '\\"').replace("\n", "\\n")
                print(f'{key}="{escaped_value}"')
        elif format == "json":
            print(json.dumps(secrets, indent=2))
        else:
            print(f"Error: Unknown format '{format}'", file=sys.stderr)
            raise typer.Exit(1)

    except Exception as e:
        if "No secrets found" not in str(e):
            print(f"Error: Export failed: {e}", file=sys.stderr)
        raise typer.Exit(1)


@secrets_app.callback(invoke_without_command=True)
def secrets_main(
    ctx: typer.Context,
) -> None:
    """Manage secrets in the datalake.

    Store and retrieve secrets securely in your datalake.
    Secrets are encrypted and versioned automatically.

    Examples:
        dkdc secrets set API_KEY          # Interactive prompt
        dkdc secrets get API_KEY          # Output value only
        dkdc secrets list                 # List all secrets
        dkdc secrets export -f dotenv     # Export as .env
    """
    if ctx.invoked_subcommand is None:
        from rich.console import Console

        console = Console()
        console.print("\n🔐 [bold]dkdc secrets[/bold] - Secure secret management\n")
        print(ctx.get_help())
        raise typer.Exit()
