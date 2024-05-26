# imports
import tiktoken

from dkdc.defaults import OPENAI_MODEL


# functions
def str_to_tokens(text: str, model: str = OPENAI_MODEL) -> list[int]:
    """
    tokenize text
    """
    enc = tiktoken.encoding_for_model(model)

    return enc.encode(text)
