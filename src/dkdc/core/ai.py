import os
import openai

from dkdc.defaults import OPENAI_MODEL
from dkdc.utils.vars import load_vars


def chat(text: str):
    """
    chat
    """
    load_vars()

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": text},
    ]

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.0,
    )

    return response.choices[0].message.content
