import os

# configuration
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".dkdc", "config.toml")
DOTENV_PATH = os.path.join(os.path.expanduser("~"), ".dkdc", ".env")

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        f.write(
            '[open.aliases]\ndk = "dkdc"\n"dc = "dkdc"\n\n[open.things]\ndkdc = "https://dkdc.dev"\n'
        )
if not os.path.exists(DOTENV_PATH):
    with open(DOTENV_PATH, "w") as f:
        f.write("")

# ai
OPENAI_MODEL = "gpt-4o"
