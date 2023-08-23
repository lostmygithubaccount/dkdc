# imports
import os
import sys
import toml
import typer


from dotenv import load_dotenv
from typing_extensions import Annotated

# local imports
from dkdc.poker import poker_total
from dkdc.resize import resize_image
from dkdc.testing import testing_run
from dkdc.translate import translate_run

# configuration
# load .env file
load_dotenv()

# load config
try:
    config = toml.load("config.toml")
except FileNotFoundError:
    config = {}

# typer config
app = typer.Typer(no_args_is_help=True)


# global options
def version(value: bool):
    if value:
        version = toml.load("pyproject.toml")["project"]["version"]
        typer.echo(f"{version}")
        raise typer.Exit()


# subcommands
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


@app.command()
def translate(
    text: Annotated[
        str, typer.Argument(help="text to translate")
    ] = "hello, try passing in a string to translate",
    to: Annotated[str, typer.Option(help="language to translate to")] = None,
    from_: Annotated[
        str, typer.Option("--from", help="language to translate from")
    ] = None,
):
    """
    translate from one language to another
    """
    if "translate" in config:
        if to is None:
            if "translate" in config and "to" in config["translate"]:
                to = config["translate"]["to"]
        if from_ is None:
            if "translate" in config and "from" in config["translate"]:
                from_ = config["translate"]["from"]

    translate_run(text=text, to=to, from_=from_)


@app.command()
def test():
    """
    test
    """
    testing_run()


# main
@app.callback()
def main(
    version: bool = typer.Option(
        None, "--version", help="Show version.", callback=version, is_eager=True
    ),
):
    # Do other global stuff, handle other global options here
    return


## main
if __name__ == "__main__":
    typer.run(main)
