"""Utilities for CLI console output with Rich styling."""

from contextlib import contextmanager
from typing import Any, Generator, Optional

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
        transient=True,
    )


@contextmanager
def spinner_task(
    description: str, success_message: Optional[str] = None
) -> Generator[None, None, None]:
    """Context manager for spinner tasks that cleans up and shows success message."""
    with create_spinner_progress() as progress:
        progress.add_task(description)
        try:
            yield
            if success_message:
                print_success(success_message)
        except Exception as e:
            print_error(f"Failed: {description.lower()}", str(e))
            raise


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


@contextmanager
def operation_progress(
    description: str, success_message: str
) -> Generator[Progress, None, None]:
    """Context manager for multi-step operations with clean completion."""
    with create_spinner_progress() as progress:
        progress.add_task(description)
        try:
            yield progress
            print_success(success_message)
        except Exception as e:
            print_error(f"Failed: {description.lower()}", str(e))
            raise


def check_and_report_duckdb() -> None:
    """Check if duckdb CLI is available and print installation help if not."""
    from dkdc.config import DUCKDB_INSTALL_URL
    from dkdc.datalake.utils import check_duckdb

    if not check_duckdb():
        print_error("Missing prerequisite")
        console.print(f"  - duckdb CLI: {DUCKDB_INSTALL_URL}")
        console.print("Please install duckdb CLI and try again.")
        raise RuntimeError("duckdb CLI not found")


def ensure_setup_with_feedback(quiet: bool = False) -> None:
    """Ensure database setup with user feedback."""
    from dkdc.datalake.utils import ensure_setup

    if not quiet:
        console.print("🗃️ Setting up database...")

    try:
        ensure_setup()
        if not quiet:
            console.print("✅ Database is ready!")
    except Exception as e:
        if not quiet:
            print_error("Failed to set up database", str(e))
        raise
