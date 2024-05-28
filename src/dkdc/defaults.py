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
DATABASE_PATH = os.path.join(os.path.expanduser("~"), ".dkdc", "database.ddb")

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        f.write(CONFIG_FILE)
if not os.path.exists(DOTENV_PATH):
    with open(DOTENV_PATH, "w") as f:
        f.write(ENV_FILE)

# ai defaults
OPENAI_MODEL = "gpt-4o"
