# imports
import re
import os
import toml
import typer
import openai
import marvin

import logging as log

from marvin import ai_fn, ai_model, ai_classifier, AIApplication
from rich.console import Console
from dotenv import load_dotenv

## local imports
from dkdc.common import dkdcai

# setup console
console = Console()

# setup AI
chatbot = AIApplication(
    description=(
        "A chatbot that always speaks in brief rhymes. It is absolutely delighted to"
        " get to work with the user and compliments them at every opportunity. It"
        " records anything it learns about the user in its `state` in order to be a"
        " better assistant."
    )
)


# testing
def testing_run():
    dkdcai(end="")
    console.print(f"done...")

    response = chatbot("Hello! Do you know how to sail?")
    console.print(response.content + "\n")

    response = chatbot("What about coding?")
    console.print(response.content)
