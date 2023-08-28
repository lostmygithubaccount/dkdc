import toml
import typer
import marvin

import logging as log

from dotenv import load_dotenv

from marvin import ai_fn, ai_model, ai_classifier, AIApplication
from marvin.prompts.library import System, User, ChainOfThought
from marvin.engine.language_models import chat_llm

from typing import Optional

## local imports
from dkdc.utils import *
from dkdc.tools import *
from dkdc.systems import *

# AI class
class AI:
    def __init__(self):
        # load env
        load_dotenv()

        # setup AI
        model = "azure_openai/gpt-4-32k"
        marvin.settings.llm_model = model
        model = chat_llm(model)

        # construct AI
        dkdcai = AIApplication(
            description=(
                "You are the bot that can do anything."
                "You can roll dice."
                "You can read and write files."
                "You can run commands in the terminal."
                "Never forget to use the aliases."
            ),
            tools=[read_file, roll_dice, run_command, list_files],
            additional_prompts=[prompt2, prompt, prompt3],
        )

        # setup self
        self.ai = dkdcai
        self.console = Console()

    def __call__(self, text):
        dkdconsole(end="", blink="blink")
        console.print(self.ai(text).content)

    @property
    def tools(self):
        return self.ai.tools

    @property
    def history(self):
        return self.ai.history

    @property
    def additional_prompts(self):
        return self.ai.additional_prompts


ai = AI()
