# imports
import os
import sys
import toml
import typer

from dotenv import load_dotenv

## local imports
from .poker import poker_total
from .resize import resize_image

# configuration
## load .env file
load_dotenv()

## load config
try:
    config = toml.load("config.toml")
except FileNotFoundError:
    config = {}

## typer config
app = typer.Typer(no_args_is_help=True)

## global options
def version(value: bool):
    if value:
        version = toml.load("pyproject.toml")["project"]["version"]
        typer.echo(f"{version}")
        raise typer.Exit()


## subcommands
@app.command()
def poker():
    """
    poker
    """
    poker_total()


@app.command()
def resize(
    filename: str = "thumbnail.png", output: str = "thumbnail.png", size: int = 256
):
    """
    resize an image
    """
    resize_image(filename, output, size)


## main
@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", help="Show version.", callback=version, is_eager=True
    ),
):
    # Do other global stuff, handle other global options here
    return


## if __name__ == "__main__":
if __name__ == "__main__":
    typer.run(main)
