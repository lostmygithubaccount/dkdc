# imports
import os
import sys
import typer
import tomllib as toml


from dotenv import load_dotenv
from typing_extensions import Annotated

# load .env file
# TODO: better
load_dotenv(os.path.expanduser("~/.dkdc/.env"))

# load config
# TODO: better
# try:
#     config = toml.load(os.path.expanduser("~/.dkdc/config.toml"))
# except FileNotFoundError:
config = {}

# typer config
app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.command()
def hello():
    """
    hello
    """
    print("hello")


# main
@app.callback()
def cli(
    # version: bool = typer.Option(
    #     None, "--version", help="Show version.", callback=version, is_eager=True
    # ),
):
    return


## main
if __name__ == "__main__":
    typer.run(cli)
