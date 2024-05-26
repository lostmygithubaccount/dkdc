# imports
import subprocess

from dkdc.cli.console import print
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

    print(f"opening {thing}...")
    subprocess.call(["open", thing])


def list_things() -> None:
    """
    list things
    """
    config = load_config()

    aliases = []
    things = []

    for alias, thing in config["open"]["aliases"].items():
        aliases.append((alias, thing))

    for thing in config["open"]["things"]:
        things.append((thing, config["open"]["things"][thing]))

    aliases.sort(key=lambda x: (len(x[0]), x[0]))
    things.sort(key=lambda x: (len(x[0]), x[0]))

    alias_max = max([len(alias) for alias, _ in aliases])
    thing_max = max([len(thing) for thing, _ in things])

    to_print = "aliases:\n"
    for alias, thing in aliases:
        to_print += f"  - {alias.ljust(alias_max)} | {thing}\n"

    to_print += "\n\nthings:\n"
    for thing, path in things:
        to_print += f"  - {thing.ljust(thing_max)} | {path}\n"

    print(to_print)
