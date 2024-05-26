# imports
import subprocess

from dkdc.defaults import CONFIG_PATH, DOTENV_PATH
from dkdc.cli.console import print


# functions
def config_it(vim: bool, env: bool) -> None:
    """
    open a config file
    """
    program = "nvim" if vim else "code"
    filename = DOTENV_PATH if env else CONFIG_PATH

    print(f"opening {filename} with {program}...")
    subprocess.call([program, f"{filename}"])
