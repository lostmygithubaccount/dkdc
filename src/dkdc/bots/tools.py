import os
import sys
import random
import requests
import webbrowser

from io import StringIO

from itertools import islice
from html2text import html2text
from duckduckgo_search import DDGS

from dkdc.tools import tool
from dkdc.bots.utils import *
from dkdc.bots.models import *
from dkdc.bots.functions import *
from dkdc.bots.classifiers import *
from dkdc.bots.summarize.ai import SummarizeWebpageBot


# tools
@tool
def search_internet(
    query: str = "what is dkdc.dev?", n_results: int = 8
) -> list[dict[str, str | None]]:
    """
    Searches the internet for the given query.
    """
    ddgs = DDGS()
    return [r for r in islice(ddgs.text(query, backend="lite"), n_results)]


@tool
def summarize_page(url: str) -> str:
    """
    Summarizes a webpage given a url.
    """
    bot = SummarizeWebpageBot()
    return bot(url)


@tool
def webpage_to_str(url: str = "https://dkdc.dev") -> str:
    """
    Reads a webpage via URL into a string.
    """
    response = requests.get(url)
    return html2text(response.text)


@tool
def open_url_in_browser(url: str = "https://dkdc.dev") -> str:
    """
    Opens a URL in the default browser.
    """
    webbrowser.open(url)
    return "Opened in browser."


@tool
def create_python_function(task: str = "print('hello world')", name: str = "fn") -> str:
    """
    Creates a Python function with the given name
    to accomplish the given task.
    """
    return create_function(task=task, name=name, language="Python")


@tool
def list_files(path: str = ".", depth: int = 2, additional_ignore_dirs: list = []):
    """
    Lists all files in a directory.
    """
    path = os.path.expanduser(path)
    files_list = []
    home = os.path.expanduser("~")
    gitignore_path = os.path.join(home, ".gitignore")

    if os.path.exists(gitignore_path):
        gitignore_patterns = read_gitignore(gitignore_path)
    else:
        gitignore_patterns = []

    ignore_dirs = [".git"] + additional_ignore_dirs

    for root, dirs, files in os.walk(path):
        if root.count(os.sep) >= depth:
            dirs.clear()  # Clear directories list to prevent further depth traversal.

        dirs[:] = [
            d
            for d in dirs
            if not is_ignored(d, ignore_dirs) and not is_ignored(d, gitignore_patterns)
        ]

        for file in files:
            file_path = os.path.join(root, file)
            if not is_ignored(file_path, gitignore_patterns):
                files_list.append(file_path)
    return files_list


@tool
def roll_dice(n_dice: int = 1) -> list[int]:
    """
    Rolls a dice n times and returns the result as a list.
    """
    return [random.randint(1, 6) for _ in range(n_dice)]


@tool
def read_file(path: str) -> str:
    """
    Reads a file and returns its content.
    """
    path = os.path.expanduser(path)
    with open(path, "r") as f:
        return f.read()


@tool
def run_python(code: str):
    """
    Runs Python code and returns the result.
    """
    old_stdout = sys.stdout
    new_stdout = StringIO()
    sys.stdout = new_stdout
    try:
        exec(code)
        result = new_stdout.getvalue()
    except Exception as e:
        result = repr(e)
    finally:
        sys.stdout = old_stdout
    return result


@tool
def run_command(command: str = "echo 'pass in a command to run as a string'") -> int:
    """
    Runs a command in the terminal.
    """
    return os.system(f"{command}")
