# imports
import typer

## local imports
from dkdc.ai import tokenize_it
from dkdc.open import open_it, list_things
from dkdc.image import resize_image
from dkdc.config import config_it

# typer config
## default kwargs
default_kwargs = {
    "no_args_is_help": True,
    "add_completion": False,
}

## main app
app = typer.Typer(help="dkdc", **default_kwargs)

## subcommands
ai_app = typer.Typer(help="ai subcommands", **default_kwargs)
image_app = typer.Typer(help="image subcommands", **default_kwargs)

## add subcommands
app.add_typer(ai_app, name="ai")
app.add_typer(image_app, name="image")

## add subcommand aliases
app.add_typer(ai_app, name="ml", hidden=True)
app.add_typer(image_app, name="i", hidden=True)


# commands
@app.command()
@app.command("c", hidden=True)
def config(
    vim: bool = typer.Option(False, "--vim", "-v", help="Open with (n)vim."),
    env: bool = typer.Option(False, "--env", "-e", help="Open .env file."),
):
    """
    open config file
    """
    config_it(vim, env)


@app.command()
@app.command("o", hidden=True)
def open(
    thing: str = typer.Argument(None, help="Thing to open."),
):
    """
    open thing
    """
    if thing is None:
        list_things()
    else:
        open_it(thing)


## image commands
@ai_app.command()
@ai_app.command("t", hidden=True)
def tokenize(text: str = typer.Argument(..., help="Text to tokenize.")):
    """
    tokenize text
    """
    tokens = tokenize_it(text)
    print(text, end=" -> ")
    print(tokens)


@image_app.command()
def resize(
    input_path: str = typer.Argument("thumbnail.png"),
    output_path: str = typer.Argument("resized.png"),
    height: int = typer.Option(256, "--height", "-h", help="Height of the image."),
    width: int = typer.Option(256, "--width", "-w", help="Width of the image."),
):
    """
    resize an image
    """
    resize_image(input_path, output_path, height, width)


# main
@app.callback()
def cli():
    return


# main
if __name__ == "__main__":
    typer.run(cli)
