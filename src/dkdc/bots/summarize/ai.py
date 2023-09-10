# imports
import marvin

import logging as log

from marvin import AIApplication

from rich.console import Console

from dkdc.bots.summarize.tools import *
from dkdc.bots.summarize.states import *
from dkdc.bots.summarize.systems import *


# AI class
class SummarizeWebpageBot:
    def __init__(self) -> None:
        # setup AI
        model = "azure_openai/gpt-4-32k"
        marvin.settings.llm_model = model

        # construct AI
        state = State()
        prompts = []
        tools = [url_to_str, summarize_text]
        ai = AIApplication(
            description=main_system,
            state=state,
            tools=tools,
            additional_prompts=prompts,
        )

        # setup self
        self.ai = ai

    def __call__(self, url: str):
        ai_input = f"Read the webpage and summarize its content: {url}"
        return self.ai(ai_input).content
