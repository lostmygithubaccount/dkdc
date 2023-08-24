from rich import console

console = console.Console()


def dkdcai(end="\n", blink=""):
    console.print("dkdc.ai", style=f"{blink} bold violet", end="")
    console.print(": ", style="bold white", end=end)
