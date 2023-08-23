from rich.console import Console

console = Console()


def dkdcai(end="\n", blink=""):
    console.print("dkdc.ai", style=f"{blink} bold violet", end="")
    console.print(": ", style="bold white", end=end)
