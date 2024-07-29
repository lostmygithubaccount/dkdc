# imports
import tiktoken

from dkdc.defaults import OPENAI_MODEL
from tiktoken.load import load_tiktoken_bpe


# functions
def str_to_tokens2(text: str, model: str = OPENAI_MODEL) -> list[int]:
    """
    tokenize text
    """
    enc = tiktoken.encoding_for_model(model)

    return enc.encode(text)


def get_tokenizer():
    """
    tokenize text
    """
    # https://levelup.gitconnected.com/building-llama-3-from-scratch-with-python-e0cf4dbbc306
    tokenizer_model = load_tiktoken_bpe(
        "llama-models/models/llama3_1/Meta-Llama-3.1-8B-Instruct/tokenizer.model"
    )
    special_tokens = [
        "<|begin_of_text|>",  # Marks the beginning of a text sequence.
        "<|end_of_text|>",  # Marks the end of a text sequence.
        "<|reserved_special_token_0|>",  # Reserved for future use.
        "<|reserved_special_token_1|>",  # Reserved for future use.
        "<|reserved_special_token_2|>",  # Reserved for future use.
        "<|reserved_special_token_3|>",  # Reserved for future use.
        "<|start_header_id|>",  # Indicates the start of a header ID.
        "<|end_header_id|>",  # Indicates the end of a header ID.
        "<|reserved_special_token_4|>",  # Reserved for future use.
        "<|eot_id|>",  # Marks the end of a turn (in a conversational context).
    ] + [
        f"<|reserved_special_token_{i}|>" for i in range(5, 256 - 5)
    ]  # A large set of tokens reserved for future use.
    #  patterns based on which text will be break into tokens
    tokenize_breaker = r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\n\p{L}\p{N}]?\p{L}+|\p{N}{1,3}| ?[^\s\p{L}\p{N}]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+"
    # Initialize tokenizer with specified parameters
    tokenizer = tiktoken.Encoding(
        # make sure to set path to tokenizer.model file
        name="tokenizer.model",
        # Define tokenization pattern string
        pat_str=tokenize_breaker,
        # Assign BPE mergeable ranks from tokenizer_model of LLaMA-3
        mergeable_ranks=tokenizer_model,
        # Set special tokens with indices
        special_tokens={
            token: len(tokenizer_model) + i for i, token in enumerate(special_tokens)
        },
    )

    return tokenizer


def str_to_tokens(text: str, model: str) -> list[int]:
    tokenizer = get_tokenizer()
    return tokenizer.encode(text)
