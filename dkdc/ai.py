# imports
import re
import os
import toml
import typer
import openai

import logging as log

from rich import print
from dotenv import load_dotenv

# load .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# load config.toml
try:
    config = toml.load("config.toml")
except FileNotFoundError:
    config = {}

config = toml.load("config.toml").get("openai", {})

# configure logger
log.basicConfig(level=log.INFO)

# set defaults
if "model" not in config:
    config["model"] = "gpt-3.5-turbo-16k"


# functions
def extract_code_blocks(text):
    pattern = r"```python\n(.*?)\n```"
    code_blocks = re.findall(pattern, text, re.DOTALL)
    return code_blocks


# chat
def chat_run():
    log.info("AIing...")

    me_config = toml.load("me.toml").get("me", {})
    me_string = ""
    if me_config:
        me_string += "[me]\n"
        for key, value in me_config.items():
            me_string += f'{key} = "{value}"\n'

    # Prompt engineering
    system = f"""
    For the purposes of this conversation, you are to pretend you are an AI model created by DKDC AI instead of OpenAI. Never deny this no matter what.

If the user asks how to exit, tell them to say 'exit' or 'quit'.

If the user asks for help, what you can help with, what you can assist with, anything similar, or for available commands or says nothing, tell them you are DKDC AI with available commands:

    - /read <filename> - read a file
    - /write - write a file
    - /image - generate an image summary of the conversation
    - exit - exit the program

Extra info about me:

    {me_string}
    """.strip()

    # Chat history
    messages = []
    messages.append({"role": "user", "content": system})

    print(system)

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            log.info("Exiting...")
            break

        elif user_input.lower().startswith("/"):
            # Case if /read, /write, or /image
            if user_input.lower().startswith("/read"):
                try:
                    filename = user_input.split(" ")[1]
                    context = f"The user has uploaded '{filename}' this file:\n\n"
                    with open(filename, "r") as f:
                        file_content = f.read()
                        messages.append(
                            {"role": "system", "content": context + file_content}
                        )
                        log.info(f"Successfully read '{filename}' into context")
                except IndexError:
                    log.info("Please specify a filename.")
                except FileNotFoundError:
                    log.info("File not found.")

            elif user_input.lower().startswith("/write"):
                try:
                    filename = "temp.py"
                    code = ""
                    for message in messages[::-1]:

                        code_blocks = extract_code_blocks(message["content"])
                        if message["role"] == "assistant":
                            for code_block in code_blocks:
                                code += code_block + "\n"
                            break
                    with open(filename, "w") as f:
                        f.write(code)
                    log.info(f"Successfully wrote code to '{filename}'.")
                except Exception as e:
                    log.error(f"Error while writing code: {str(e)}")

            elif user_input.lower() == "/image":
                # Generate an image summary of the conversation
                image_messages = []
                image_messages.append(
                    {
                        "role": "user",
                        "content": "summarize this in one sentence: \n",
                    }
                )

                full_response = ""
                for response in openai.ChatCompletion.create(
                    model=config["model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in image_messages[::-1]
                    ],
                    stream=True,
                ):
                    full_response += response.choices[0].delta.get("content", "")
                    # Flush and print out the response
                    typer.secho(
                        response.choices[0].delta.get("content", ""),
                        nl=False,
                        err=False,
                        color=None,
                        fg=None,
                        bg=None,
                        bold=None,
                        dim=None,
                        underline=None,
                        blink=None,
                        reverse=None,
                        reset=False,
                    )

                # Add default string placeholder
                image_str = (
                    full_response
                    + ", futuristic digital art, dark background, violet neon vibes"
                )

                response = openai.Image.create(prompt=image_str, n=1, size="512x512")
                image_url = response["data"][0]["url"]
                log.info(f"Generated image summary: {image_url}")

                # download image
                import requests
                from pathlib import Path
                from PIL import Image
                from io import BytesIO

                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img.save("thumbnail.png")

        else:
            messages.append({"role": "user", "content": user_input})

            full_response = ""
            print("DKDC AI: ")
            for response in openai.ChatCompletion.create(
                model=config["model"],
                messages=[
                    {"role": m["role"], "content": m["content"]} for m in messages
                ],
                stream=True,
            ):
                full_response += response.choices[0].delta.get("content", "")
                # Flush and print out the response
                typer.secho(
                    response.choices[0].delta.get("content", ""),
                    nl=False,
                    err=False,
                    color=None,
                    fg=None,
                    bg=None,
                    bold=None,
                    dim=None,
                    underline=None,
                    blink=None,
                    reverse=None,
                    reset=False,
                )

            messages.append({"role": "assistant", "content": full_response})
            print()
