# imports
import re
import os
import json
import toml
import ibis
import typer
import openai
import marvin
import random

import logging as log

from dotenv import load_dotenv

from typing import Optional

from marvin import ai_fn, ai_model, ai_classifier, AIApplication
from marvin.prompts.library import System, User, ChainOfThought
from marvin.engine.language_models import chat_llm

from rich import print
from rich.console import Console

from dkdc.dkdc import ai
from dkdc.poker import *

# configure ibis
ibis.options.interactive = True

# load dotenv
load_dotenv()

# create connection
con = ibis.connect("duckdb://cache.ddb")
tables = con.list_tables()

hands = play_poker()
s = hands
data = [history_to_dict(t) for t in hands]
t = data[-1]
