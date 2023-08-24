# imports
import os
import toml
import typer
import marvin
import requests

import logging as log

from rich import console

from marvin import ai_fn, ai_model
from pydantic import BaseModel, Field
from marvin.engine.language_models import chat_llm

## local imports
from dkdc.common import dkdcai

# configure output
console = console.Console()

# configure ai
marvin.settings.llm_model = "azure_openai/gpt-4"


@ai_fn
def translate(text: str = "hello", to: str = "Spanish", from_: str = "English") -> str:
    """Translate text from one language to another"""


# translate
def translate_run(text, to, from_):
    dkdcai(end="")
    console.print("Starting advanced AI translation...")

    log.info(f"to: {to}")
    log.info(f"from: {from_}")
    log.info(f"text: {text}")

    # translate
    console.print(f"Original text:\n{text}")
    translated_text = translate(text, to, from_)
    console.print(f"Translated text:\n{translated_text}")
