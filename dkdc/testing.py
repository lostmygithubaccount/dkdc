# imports
import re
import os
import toml
import typer
import openai
import marvin

import logging as log

from marvin import ai_fn, ai_model
from rich import print
from rich.console import Console
from dotenv import load_dotenv

## local imports
from dkdc.common import dkdcai

# configure output
console = Console()


# testing
def testing_run():
    dkdcai(end="")
    console.print(f"\ndone...")
