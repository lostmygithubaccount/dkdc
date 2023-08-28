from rich import console

console = console.Console()


def dkdconsole(end="\n", blink=""):
    console.print("dkdc.dev", style=f"{blink} bold violet", end="")
    console.print(": ", style="bold white", end=end)
