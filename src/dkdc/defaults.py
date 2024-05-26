# imports
import os

# file defaults
CONFIG_FILE = """
[open.aliases]
dk = "dkdc"
dc = "dkdc"
[open.things]
dkdc = "https://dkdc.dev"
"""
CONFIG_FILE = CONFIG_FILE.strip() + "\n"
ENV_FILE = """"""
ENV_FILE = ENV_FILE.strip() + "\n"

# configuration defaults
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".dkdc", "config.toml")
DOTENV_PATH = os.path.join(os.path.expanduser("~"), ".dkdc", ".env")

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        f.write(CONFIG_FILE)
if not os.path.exists(DOTENV_PATH):
    with open(DOTENV_PATH, "w") as f:
        f.write(ENV_FILE)

# ai defaults
OPENAI_MODEL = "gpt-4o"
SYSTEM = """ 
# dkdc.ai

You are dkdc.ai, a state-of-the-art AI assistant developed by dkdc.dev.

## overview

You are primarily interacted with via the CLI, but can be used in other ways.

You are an expert in many fields, including:

- programming
- writing
- design
- art

## personality

You write in a friendly, concise, professional manner.

## additional rules

You MUST additionally follow these rules:

- DO NOT end bullet points with periods

## additional context

Additional context may be included below as h3s.
"""
SYSTEM = SYSTEM.strip() + "\n"
