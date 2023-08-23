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
from dkdc.common import dkdcai

# load .env file
load_dotenv()

# load config.toml
config = {}
try:
    config = toml.load("config.toml")["translate"]
except:
    pass

# variables
console = Console()

marvin.settings.llm_model = "azure_openai/gpt-4"


@ai_fn
def mathai(equation: str) -> float:
    """Solve a math equation. Guess if you don't know."""


def mathai_run():
    pass
