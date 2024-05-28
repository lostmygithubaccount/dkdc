# imports
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown

# console
console = Console()

# style map
style_map = {
    "dkdc": "bold white",
    "user": "bold cyan",
    "dkdc.ai": "bold violet",
}


# functions
def print(
    text: str, as_markdown: bool = True, as_panel: bool = True, header: str = "dkdc"
) -> None:
    """
    print text
    """
    if as_markdown:
        text = Markdown(text)

    if as_panel:
        text = Panel(text, title=header, border_style=style_map[header])

    console.print(text)
