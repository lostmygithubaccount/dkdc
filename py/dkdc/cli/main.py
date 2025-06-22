"""Main CLI application for dkdc."""

# Imports
import typer

from dkdc.cli.archive import archive_app
from dkdc.cli.backup import backup_app
from dkdc.cli.dev import dev_app
from dkdc.cli.files import files_app
from dkdc.cli.secrets import secrets_app
from dkdc.config.config import open_config
from dkdc.config.constants import migrate_legacy_lake_directory

# Configuration
app = typer.Typer(name="dkdc", add_completion=False)

app.add_typer(archive_app, name="archive")
app.add_typer(backup_app, name="backup")
app.add_typer(dev_app, name="dev")
app.add_typer(files_app, name="files")
app.add_typer(secrets_app, name="secrets")


@app.callback(invoke_without_command=True)
def cli_callback(
    ctx: typer.Context,
    config: bool = typer.Option(
        False,
        "--config",
        "-c",
        help="Open config file in editor",
    ),
) -> None:
    """dkdc: don't know, don't care."""
    # Run migration check on every CLI invocation
    migrate_legacy_lake_directory()

    if config:
        open_config()
        return

    if ctx.invoked_subcommand is None:
        print(ctx.get_help())
        raise typer.Exit()


# Functions
def main() -> None:
    app()


# Entry point
if __name__ == "__main__":
    main()
