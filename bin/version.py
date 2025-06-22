#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typer",
#     "rich",
# ]
# ///
"""
Bump version in pyproject.toml.
"""

import re
import tomllib
from pathlib import Path

import typer
from rich.console import Console

# Config
app = typer.Typer(add_completion=False, help="Bump `pyproject.toml` version")
console = Console()

# Functions


@app.command()
def main(
    major: bool = typer.Option(False, "--major", help="Bump major version"),
    minor: bool = typer.Option(False, "--minor", help="Bump minor version"),
) -> None:
    """Bump version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.exists():
        console.print("[red]Error: pyproject.toml not found[/red]")
        raise typer.Exit(1)

    # Read current version
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    current_version = data.get("project", {}).get("version", "0.0.0")

    # Parse version
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", current_version)
    if not match:
        console.print(f"[red]Error: Invalid version format: {current_version}[/red]")
        raise typer.Exit(1)

    major_num, minor_num, patch_num = map(int, match.groups())

    # Bump version
    if major:
        major_num += 1
        minor_num = 0
        patch_num = 0
    elif minor:
        minor_num += 1
        patch_num = 0
    else:
        patch_num += 1

    new_version = f"{major_num}.{minor_num}.{patch_num}"

    # Update file
    content = pyproject_path.read_text()
    updated_content = re.sub(
        r'^(version\s*=\s*")[^"]+"',
        rf'\g<1>{new_version}"',
        content,
        flags=re.MULTILINE,
    )

    pyproject_path.write_text(updated_content)

    console.print(f"[green]✓[/green] Bumped version: {current_version} → {new_version}")


# Entry point
if __name__ == "__main__":
    app()
