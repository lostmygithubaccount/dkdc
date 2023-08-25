# imports
import re
import os
import toml
import typer
import openai
import marvin
import random

import logging as log

from rich.console import Console
from dotenv import load_dotenv

from marvin import ai_fn, ai_model, ai_classifier, AIApplication
from marvin.tools import tool
from marvin.prompts.library import System, User, ChainOfThought
from marvin.engine.language_models import chat_llm

from typing import Optional

## local imports
from dkdc.common import dkdcai

# load env
load_dotenv()

# setup console
console = Console()

# setup AI
model = "azure_openai/gpt-4"
marvin.settings.llm_model = model
model = chat_llm(model)


class ReActPattern(System):
    content = """
    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    Use Thought to describe your thoughts about the question you have been asked.
    Use Action to run one of the actions available to you - then return PAUSE.
    Observation will be the result of running those actions.
    """

class ExpertSystem(System):
    content: str = (
        "You are a world-class expert on {{ topic }}. "
        "When asked questions about {{ topic }}, you answer correctly. "
        "You only answer questions about {{ topic }}. "
    )
    topic: Optional[str]


class Tutor(System):
    content: str = (
        "When you give an answer, you modulate your response based on the "
        "inferred knowledge of the user. "
        "Your student's name is {{ name }}. "
        "Your student's knowledge level is {{ knowledge_level }}/10. "
    )
    name: str = "not provided"
    knowledge_level: int = 5

class CodeOutput(System):
    content: str = (
        "You output code in {{ language }} to demonstrate the concept. "
        "For Python use Ibis, the dataframe library. "
    )
    language: str = "Python"

response = model(
    (
        ExpertSystem()
        | Tutor()
        | User(
            "What are CTEs?"
        )
        | ChainOfThought()
        #| ReActPattern()
        | CodeOutput()
    ).render(topic="SQL", name="Cody", language="Python")
)

# functions
@tool
def roll_dice(n_dice: int = 1) -> list[int]:
    return [random.randint(1, 6) for _ in range(n_dice)]


# configure ai
marvin.settings.llm_model = "azure_openai/gpt-4"
chatbot = AIApplication(
    description=(
        "A chatbot that always speaks in brief rhymes. It is absolutely delighted to"
        " get to work with the user and compliments them at every opportunity. It"
        " records anything it learns about the user in its `state` in order to be a"
        " better assistant."
        "Roll dice if asked."
    ),
    tools = [roll_dice],
    # stream_handler=lambda msg: console.print(msg.content, end="")
)
