# imports
import re
from rich import console

# setup console
console = console.Console()

# functions
def poker_total():
    path = "poker.md"
    total = 0
    pattern = r"\d{1,2}\/\d{1,2}:\s*([+-]?\d+)"

    with open(path, "r") as file:
        contents = file.read()
        matches = re.findall(pattern, contents)
        for match in matches:
            num = int(match)
            total += num

    color = "green" if total >= 0 else "red"
    console.print(f"[bold {color}]Earnings: {total}[/bold {color}]")
