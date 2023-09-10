# imports
import marvin

import logging as log

from marvin import AIApplication

from rich.console import Console

from dkdc.bots.dkdc.tools import *
from dkdc.bots.dkdc.models import *
from dkdc.bots.dkdc.states import *
from dkdc.bots.dkdc.systems import *
from dkdc.bots.dkdc.functions import *
from dkdc.bots.dkdc.classifiers import *


# AI class
class AI:
    def __init__(self, con=None, additional_prompts=[], additional_tools=[]) -> None:
        # setup AI
        model = "azure_openai/gpt-4-32k"
        marvin.settings.llm_model = model

        # construct AI
        state = State()
        prompts = [Yolo(), Internet()]
        prompts += additional_prompts
        tools = [
            create_python_function,
            run_python,
            read_file,
            roll_dice,
            run_command,
            list_files,
            search_internet,
            summarize_page,
            open_url_in_browser,
        ]
        tools += additional_tools
        ai = AIApplication(
            description=main_system,
            state=state,
            tools=tools,
            additional_prompts=prompts,
        )

        # setup self
        self.ai = ai
        self.con = con
        self.console = Console()

    def __call__(self, text):
        self.console.print("dkdc.ai: ", style="bold violet blink", end="")
        self.console.print(self.ai(text).content)

    @property
    def history(self):
        return self.ai.history

    @property
    def state(self):
        return self.ai.state

    @property
    def tools(self):
        return self.ai.tools

    @property
    def additional_prompts(self):
        return self.ai.additional_prompts
