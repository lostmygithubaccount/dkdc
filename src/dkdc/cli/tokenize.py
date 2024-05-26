# imports
from rich.console import Console
from dkdc.defaults import OPENAI_MODEL
from dkdc.ai.tokenize import str_to_tokens


# functions
def tokenize_it(text: str):
    """
    tokenize text
    """
    console = Console()
    tokens = str_to_tokens(text, model=OPENAI_MODEL)

    console.print(f"{text} -> {tokens}")
