from dotenv import load_dotenv

from dkdc.defaults import DOTENV_PATH


def load_vars(path: str = DOTENV_PATH) -> None:
    """
    Load environment variables from a file.
    """

    load_dotenv(path)
