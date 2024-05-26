# imports
from dkdc.defaults import OPENAI_MODEL
from dkdc.ai.tokenize import str_to_tokens
from dkdc.cli.console import print


# functions
def tokenize_it(text: str):
    """
    tokenize text
    """
    tokens = str_to_tokens(text, model=OPENAI_MODEL)
    print(f"{text} -> {tokens}")
