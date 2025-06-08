"""Main CLI application for dkdc."""

# Imports
import typer

from dkdc.cli.backup import backup_app
from dkdc.cli.dev import dev_app
from dkdc.cli.yolo import yolo_app

# Configuration
app = typer.Typer(name="dkdc", no_args_is_help=True)

app.add_typer(backup_app, name="backup")
app.add_typer(dev_app, name="dev")
app.add_typer(yolo_app, name="yolo")


# Functions
def main() -> None:
    app()


# Entry point
if __name__ == "__main__":
    main()
