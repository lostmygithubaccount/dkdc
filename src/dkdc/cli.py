# imports
import typer
import textwrap

## local imports
from dkdc.core.ai import chat
from dkdc.core.open import open_it, list_things
from dkdc.core.image import resize_image
from dkdc.core.config import config_it
from dkdc.core.tokenize import tokenize_it

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
def ai(
    text: str = typer.Argument(None, help="text to chat"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="interactive"),
):
    """
    chat with ai
    """
    if interactive:
        # TODO: conversation history
        if text is None:
            text = typer.prompt("user")
        while text not in ["exit", "e", "quit", "q"]:
            response = chat(text)
            # response = textwrap.fill(response, width=80)
            print("ai: ", end="")
            print(response)
            text = typer.prompt("user")

    else:
        if text is None:
            text = typer.prompt("user")
        response = chat(text)
        # response = textwrap.fill(response, width=80)
        print("ai: ", end="")
        print(response)


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


## image commands
@app.command()
@app.command("t", hidden=True)
def tokenize(text: str = typer.Argument(..., help="text to tokenize")):
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
    height: int = typer.Option(256, "--height", "-H", help="height of the image"),
    width: int = typer.Option(256, "--width", "-W", help="width of the image"),
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
