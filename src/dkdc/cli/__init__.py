# imports
import typer

## local imports
from dkdc.cli.ai import run_ai
from dkdc.cli.open import open_it, list_things
from dkdc.cli.image import resize_image, convert_image
from dkdc.cli.config import config_it
from dkdc.cli.tokenize import tokenize_it

# typer config
## default kwargs
default_kwargs = {
    "no_args_is_help": True,
    "add_completion": False,
    "context_settings": {"help_option_names": ["-h", "--help"]},
}

## main app
app = typer.Typer(help="dkdc", **default_kwargs)

## subcommands
image_app = typer.Typer(help="image subcommands", **default_kwargs)

## add subcommands
app.add_typer(image_app, name="image")

## add subcommand aliases
app.add_typer(image_app, name="i", hidden=True)


# commands
@app.command()
@app.command("ml", hidden=True)
def ai():
    """
    chat with ai
    """
    run_ai()


@app.command()
@app.command("c", hidden=True)
def config(
    vim: bool = typer.Option(False, "--vim", "-v", help="open with (n)vim"),
    env: bool = typer.Option(False, "--env", "-e", help="open .env file"),
):
    """
    open config file(s)
    """
    config_it(vim, env)


@app.command()
@app.command("o", hidden=True)
def open(
    thing: str = typer.Argument(None, help="thing to open"),
):
    """
    open thing
    """
    if thing is None:
        list_things()
    else:
        open_it(thing)


@app.command()
@app.command("t", hidden=True)
def tokenize(text: str = typer.Argument(..., help="text to tokenize")):
    """
    tokenize text
    """
    tokenize_it(text)


## image commands
@image_app.command()
@image_app.command("r", hidden=True)
def resize(
    input_path: str = typer.Argument("thumbnail.png"),
    output_path: str = typer.Argument("resized.png"),
    height: int = typer.Option(256, "--height", "-H", help="height of the image"),
    width: int = typer.Option(256, "--width", "-W", help="width of the image"),
):
    """
    resize an image
    """
    resize_image(input_path, output_path, height, width)


@image_app.command()
@image_app.command("c", hidden=True)
def convert(
    input_path: str = typer.Argument(..., help="input path"),
    output_path: str = typer.Option(None, "--output", "-o", help="output path"),
    output_format: str = typer.Option("png", "--format", "-f", help="output format"),
):
    """
    convert an image
    """
    convert_image(input_path, output_path=output_path, output_format=output_format)


# main
if __name__ == "__main__":
    typer.run(app)
