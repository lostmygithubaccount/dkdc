# imports
import os
import json
import openai
import tiktoken


from enum import Enum
from pydantic import BaseModel, Field

from dkdc.ai.systems import DKDC_AI, DKDC_CLASSIFY, DKDC_CAST
from dkdc.ai.tokenize import str_to_tokens, get_tokenizer
from dkdc.utils import filesystem as fs
from dkdc.defaults import OPENAI_MODEL
from dkdc.utils.vars import load_vars

OPENAI_MODEL = "llama3.1:70b"


class MessageRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"


class Message(BaseModel):
    role: MessageRole
    content: str


class ChatCompletionPayload(BaseModel):
    messages: list[Message]
    model: str
    frequency_penalty: float = None
    logit_bias: dict[int, float] = None
    logprobs: bool = None
    max_tokens: int = None
    n: int = None
    presence_penalty: float = None
    response_format: str = None
    seed: int = None
    stop: str = None
    stream: bool = None
    temperature: float = None
    top_p: float = None
    tools: list[dict] | None = None
    tool_choice: dict | None = None
    user: str = None


class ResponseMessage(BaseModel):
    role: MessageRole
    content: str | None = None
    function_call: str | None = None
    tool_calls: list[dict] | None = None


class ChatCompletionResponseChoices(BaseModel):
    finish_reason: str
    index: int
    logprobs: dict | None = None
    message: ResponseMessage


class ChatCompletionResponseUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    choices: list[ChatCompletionResponseChoices]
    created: int
    model: str
    object: str
    system_fingerprint: str
    usage: ChatCompletionResponseUsage


class Client:
    def __init__(self):
        load_vars()
        sys_msg = Message(role=MessageRole.SYSTEM, content=DKDC_AI)

        # self.client = openai.OpenAI(base_url="")  # api_key=os.getenv("OPENAI_API_KEY"))
        self.client = openai.OpenAI(
            base_url="http://localhost:11434/v1", api_key="ollama"
        )
        self.messages = [sys_msg]
        self.context = {}

    def __call__(self, text: str) -> ChatCompletionResponse:
        usr_msg = Message(role=MessageRole.USER, content=text)

        self.messages.append(usr_msg)

        payload = ChatCompletionPayload(
            messages=self.messages, model=OPENAI_MODEL, temperature=0.0
        )

        response = self.client.chat.completions.create(**payload.dict())
        response = ChatCompletionResponse(**response.dict())

        resp_msg = response.choices[0].message

        self.messages.append(
            Message(
                role=MessageRole.ASSISTANT,
                content=resp_msg.content,
            )
        )

        return response

    def add_context(self, files: dict[str, str]) -> None:
        self.context = self.context | files
        self.messages[0].content += f"\n{fs.files_to_markdown(files)}"

    def reset(self) -> None:
        self.context = {}
        sys_msg = Message(role=MessageRole.SYSTEM, content=DKDC_AI)
        self.messages = [sys_msg]

    def classify(
        self,
        text: str,
        labels: list[str],
        allow_none: bool = False,
        verbose: bool = False,
        n: int = 1,
    ) -> str:
        enc = get_tokenizer()

        if allow_none:
            labels.append("None of the above")

        logit_bias = {}
        for i, _ in enumerate(labels):
            logit_bias[enc.encode(str(i))[0]] = 100.0

        text = f"{text}\nChoices:\n  {labels}"

        if verbose:
            print(f"Text: {text}")

        system = DKDC_CLASSIFY

        for i, label in enumerate(labels):
            system += f"{i}: {label}\n"

        if verbose:
            print(f"System: {system}")

        sys_msg = Message(role=MessageRole.SYSTEM, content=system)
        cls_msg = Message(role=MessageRole.USER, content=text)

        payload = ChatCompletionPayload(
            messages=[sys_msg, cls_msg],
            model=OPENAI_MODEL,
            logit_bias=logit_bias,
            max_tokens=1,
            n=n,
        )

        response = self.client.chat.completions.create(**payload.dict())
        response = ChatCompletionResponse(**response.dict())

        votes = {}
        for i, choice in enumerate(response.choices):
            if verbose:
                print(f"Response {i}:\n{choice.message.content}")
                print(f"Chose category: {labels[int(choice.message.content)]}")

            category = int(choice.message.content)
            count = votes.get(category, 0)
            votes[category] = count + 1

        if verbose:
            print(response.json())

        max_label = max(votes, key=votes.get)
        return labels[max_label]

    def cast(
        self,
        text: str,
        model_class: BaseModel,
        additional_instructions: str = None,
    ):
        system = DKDC_CAST
        if additional_instructions:
            system += f"### additional instructions\n\n{additional_instructions}"

        sys_msg = Message(role=MessageRole.SYSTEM, content=system)
        cls_msg = Message(role=MessageRole.USER, content=text)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "cast",
                    "description": "cast text into a pydantic model",
                    "parameters": model_class.schema(),
                },
            }
        ]
        tool_choice = {"type": "function", "function": {"name": "cast"}}

        payload = ChatCompletionPayload(
            messages=[sys_msg, cls_msg],
            model=OPENAI_MODEL,
            tools=tools,
            tool_choice=tool_choice,
            temperature=0.0,
        )

        response = self.client.chat.completions.create(**payload.dict())
        response = ChatCompletionResponse(**response.dict())

        class_output = json.loads(
            response.choices[0].message.tool_calls[0]["function"]["arguments"]
        )

        return model_class(**class_output)
