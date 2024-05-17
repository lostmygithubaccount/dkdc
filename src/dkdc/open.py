import subprocess

from dkdc.utils.config import load_config


def _open_it(thing: str) -> None:
    """
    _open a thing
    """
    subprocess.call(["open", thing])


def open_it(thing: str) -> None:
    """
    open a thing
    """
    config = load_config()

    if thing in config["open"]["aliases"]:
        thing = config["open"]["things"][config["open"]["aliases"][thing]]
    elif thing in config["open"]["things"]:
        thing = config["open"]["things"][thing]

    _open_it(thing)


def list_things() -> None:
    """
    list things
    """
    config = load_config()

    print("\naliases:")
    for alias, thing in config["open"]["aliases"].items():
        print(f"  - {alias}: {thing}")

    print("things:")
    for thing in config["open"]["things"]:
        print(f"  - {thing}: {config['open']['things'][thing]}")
