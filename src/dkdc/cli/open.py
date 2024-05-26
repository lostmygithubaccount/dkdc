# imports
import subprocess

from dkdc.utils.config import load_config


# functions
def open_it(thing: str) -> None:
    """
    open a thing
    """
    config = load_config()

    if thing in config["open"]["aliases"]:
        thing = config["open"]["things"][config["open"]["aliases"][thing]]
    elif thing in config["open"]["things"]:
        thing = config["open"]["things"][thing]

    subprocess.call(["open", thing])


def list_things() -> None:
    """
    list things
    """
    config = load_config()

    print("aliases:")
    for alias, thing in config["open"]["aliases"].items():
        print(f"  - {alias}: {thing}")

    print("things:")
    for thing in config["open"]["things"]:
        print(f"  - {thing}: {config['open']['things'][thing]}")
