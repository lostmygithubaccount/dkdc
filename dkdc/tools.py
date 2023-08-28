import os
import random
import fnmatch

from marvin.tools import tool
from rich.console import Console

# setup output
console = Console()


def read_gitignore(gitignore_path):
    with open(gitignore_path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if not line.startswith("#")]


def is_ignored(path, ignore_patterns):
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False


# tools
@tool
def list_files(path: str = ".", depth: int = 2, additional_ignore_dirs: list = []):
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
def read_file(filename: str, path: str = ".") -> str:
    """
    Reads a file and returns its content.
    """
    path = os.path.expanduser(path)
    with open(filename, "r") as f:
        return f.read()


@tool
def run_command(command: str = "echo 'pass in a command to run as a string'") -> int:
    """
    Runs a command in the terminal.
    """
    return os.system(f"{command}")
