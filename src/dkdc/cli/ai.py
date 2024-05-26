# imports
import typer

from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown

from dkdc.utils import filesystem as fs
from dkdc.ai.openai import Client


# functions
def run_ai(text: str = None) -> None:
    """
    chat with ai
    """
    client = Client()
    console = Console()

    if text is None:
        text = typer.prompt("user")

    text = text.strip()

    md = Markdown(text)
    console.print(Panel(md, title="user", border_style="bold cyan"))

    while text not in ["exit", "e", "quit", "q"]:
        start = text.split()[0]
        match start:
            case "load" | "l":
                try:
                    pattern = text.split()[1]
                except IndexError:
                    print("no pattern provided")
                    pattern = "src/**"

                files = fs.list_files(pattern)
                files_dict = fs.read_files(files)

                client.add_context(files_dict)

                response = f"loading pattern: {pattern}..."
                files_bullets = "\n\n- " + "\n\n- ".join(files)
                response += f"\n\nfiles: {files_bullets}"
            case "context" | "c":
                response = f"context:\n\n{fs.files_to_markdown(client.context)}"
            case "reset" | "r":
                response = "resetting context..."
                client.reset()
            case _:
                response = client(text)
                response = response.choices[0].message.content

        md = Markdown(response)
        console.print(Panel(md, title="dkdc.ai", border_style="bold violet"))

        text = typer.prompt("user")
        md = Markdown(text)
        console.print(Panel(md, title="user", border_style="bold cyan"))
