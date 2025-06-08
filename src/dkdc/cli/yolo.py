"""Yolo functionality for the dkdc CLI."""

import typer
from rich.text import Text

from dkdc.cli.utils import console

yolo_app = typer.Typer(name="yolo", no_args_is_help=False)


@yolo_app.callback(invoke_without_command=True)
def yolo_default(ctx: typer.Context) -> None:
    """Print yolo in a nice color."""
    if ctx.invoked_subcommand is None:
        yolo_text = Text("yolo", style="bold accent")
        console.print(yolo_text)
