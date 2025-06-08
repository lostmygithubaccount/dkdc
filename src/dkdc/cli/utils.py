"""Utilities for CLI console output with Rich styling."""

from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.text import Text
from rich.theme import Theme

from dkdc.config import COLORS

# Custom theme with violet/purple neon + cyan accents
DKDC_THEME = Theme(COLORS)

# Global console instance with custom theme
console = Console(theme=DKDC_THEME)


def print_header(title: str, subtitle: Optional[str] = None) -> None:
    """Print a styled header with optional subtitle."""
    header_text = Text(title, style="bold primary")
    if subtitle:
        header_text.append(f"\n{subtitle}", style="muted")

    panel = Panel(
        header_text,
        border_style="primary",
        padding=(1, 2),
    )
    console.print(panel)


def print_success(message: str, details: Optional[str] = None) -> None:
    """Print a success message with optional details."""
    text = Text("✓ ", style="success") + Text(message, style="success")
    if details:
        text.append(f"\n  {details}", style="muted")
    console.print(text)


def print_error(message: str, details: Optional[str] = None) -> None:
    """Print an error message with optional details."""
    text = Text("✗ ", style="error") + Text(message, style="error")
    if details:
        text.append(f"\n  {details}", style="muted")
    console.print(text)


def print_warning(message: str, details: Optional[str] = None) -> None:
    """Print a warning message with optional details."""
    text = Text("⚠ ", style="warning") + Text(message, style="warning")
    if details:
        text.append(f"\n  {details}", style="muted")
    console.print(text)


def print_info(message: str, details: Optional[str] = None) -> None:
    """Print an info message with optional details."""
    text = Text("ℹ ", style="secondary") + Text(message, style="primary")
    if details:
        text.append(f"\n  {details}", style="muted")
    console.print(text)


def create_progress() -> Progress:
    """Create a styled progress bar for operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold primary]{task.description}"),
        BarColumn(bar_width=None, style="primary", complete_style="success"),
        TextColumn("[muted]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
        transient=False,
    )


def create_spinner_progress() -> Progress:
    """Create a styled spinner progress for indeterminate operations."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold primary]{task.description}"),
        console=console,
        transient=False,
    )


def confirm_action(message: str, default: bool = False) -> bool:
    """Display a confirmation prompt with styled output."""
    import typer

    prompt_text = Text("? ", style="secondary") + Text(message, style="primary")
    if default:
        prompt_text.append(" [Y/n]", style="muted")
    else:
        prompt_text.append(" [y/N]", style="muted")

    console.print(prompt_text, end=" ")
    return typer.confirm("", default=default, show_default=False)


def print_key_value(
    key: str, value: Any, key_style: str = "primary", value_style: str = "muted"
) -> None:
    """Print a key-value pair with styled output."""
    text = Text(f"{key}: ", style=key_style) + Text(str(value), style=value_style)
    console.print(text)


def print_divider(text: Optional[str] = None, style: str = "muted") -> None:
    """Print a styled divider line with optional text."""
    if text:
        console.rule(text, style=style)
    else:
        console.rule(style=style)
