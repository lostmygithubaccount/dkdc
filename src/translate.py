# imports
import os
import toml
import typer
import marvin
import requests

import logging as log

from dotenv import load_dotenv
from rich.console import Console

from marvin import ai_fn, ai_model
from pydantic import BaseModel, Field
from marvin.engine.language_models import chat_llm

## local imports
from src.common import dkdcai

# load .env file
load_dotenv()

# variables
console = Console()

marvin.settings.llm_model = "azure_openai/gpt-4"


@ai_fn
def translate(text: str = "hello", to: str = "Spanish", from_: str = "English") -> str:
    """Translate text from one language to another"""


# icode
def translate_run(text, to, from_):
    dkdcai(end="")
    console.print("Starting advanced AI translation...")

    log.info(f"to: {to}")
    log.info(f"from: {from_}")
    log.info(f"text: {text}")

    # translate
    translated_text = translate(text, to, from_)
    console.print(f"Translated text:\n\n{translated_text}")
