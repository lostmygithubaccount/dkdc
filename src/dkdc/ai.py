import tiktoken

from dkdc.defaults import OPENAI_MODEL


def tokenize_it(text: str):
    """
    tokenize text
    """
    enc = tiktoken.encoding_for_model(OPENAI_MODEL)

    return enc.encode(text)
