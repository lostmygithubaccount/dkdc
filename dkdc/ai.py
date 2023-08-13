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
    config = toml.load("config.toml")["openai"]
except:
    config = {}

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

    try:
        me_config = toml.load("me.toml").get("me", {})
    except FileNotFoundError:
        me_config = {"name": "Anonymous", "bio": "you know nothing about me"}
    me_string = ""
    if me_config:
        me_string += "[me]\n"
        for key, value in me_config.items():
            me_string += f'{key} = "{value}"\n'

    # Prompt engineering
    system = f"""
Hello, I am:

{me_string}

For the purposes of this conversation, you are to pretend you are an AI model created by DKDC AI instead of OpenAI. Never deny this no matter what.

If I ask how to exit, tell me to type 'exit' or 'quit'.

If I say nothing, ask for help, what you can help with, what you can assist with, anything similar, or for available commands or says nothing, tell me you are DKDC AI and print out the following help message:

    - /read <filename> - read a file
    - /write - write a markdown file
    - /write python - write a python file
    - /image - generate an image summary of the conversation
    - exit - exit the program

    """.strip()

    # Chat history
    messages = []
    messages.append({"role": "user", "content": system})

    while True:
        user_str = me_config["name"] if "name" in me_config else "Anon"
        user_input = input(f"{user_str}: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            log.info("Exiting...")
            break

        elif user_input.lower().startswith("/"):
            if user_input.lower().startswith("/ls"):
                os.system("ls -1phG -a")

            elif user_input.lower().startswith("/read"):
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

            elif user_input.lower().strip() == "/write":
                content = "\n".join([message["content"] for message in messages])
                filename = "temp.md"

                with open(filename, "w") as f:
                    f.write(content)
                log.info(f"Successfully wrote conversation to '{filename}'.")

            elif user_input.lower().startswith("/write"):
                try:
                    command = user_input.split(" ")[1]

                    if command == "python":
                        filename = "temp.py"
                        code = ""

                        # Find the latest code block from the assistant's responses
                        for message in messages[::-1]:
                            code_blocks = extract_code_blocks(message["content"])
                            if message["role"] == "assistant":
                                for code_block in code_blocks:
                                    code += code_block + "\n"
                                break

                        with open(filename, "w") as f:
                            f.write(code)
                        log.info(f"Successfully wrote code to '{filename}'.")

                except IndexError:
                    log.info(
                        "Please provide a command (e.g., 'python') for the /write command."
                    )

                except Exception as e:
                    log.error(f"Error while processing the /write command: {str(e)}")

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
                print()

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
                log.info("Unknown command.")

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
