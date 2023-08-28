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
from dkdc.utils import dkdconsole

# configure output
console = console.Console()

# configure ai
marvin.settings.llm_model = "azure_openai/gpt-4"


@ai_fn
def math(equation: str) -> float:
    """Solve a math equation. Guess if you don't know."""


def math_run(equation):
    """Run math from the command line."""
    dkdconsole(end="")
    console.print("starting advanced AI quick mafs...")

    console.print(f"Equation: {equation}")
    result = math(equation)
    console.print(f"Result: {result}")
