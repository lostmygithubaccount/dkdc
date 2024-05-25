# imports
import tomllib

from dkdc.defaults import CONFIG_PATH


# functions
def load_config(path: str = CONFIG_PATH) -> dict:
    """
    Load a config file.
    """

    with open(path, "rb") as f:
        config = tomllib.load(f)

    return config
