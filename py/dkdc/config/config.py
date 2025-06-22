"""Configuration management for dkdc."""

import os
import subprocess
from pathlib import Path
from typing import Any, Dict

import tomllib
import typer

from .constants import get_dkdc_dir


def get_config_path() -> Path:
    """Get the path to the dkdc config file."""
    return get_dkdc_dir() / "config.toml"


def get_default_config() -> str:
    """Get the default config content."""
    return """# dkdc config file

[ducklake]
# DuckLake configuration
host = "localhost"
port = 3113
database = "dkdc"
username = "dkdc"
password = "dkdc"
schema = "dev"

# File paths
data_path = "~/.dkdc/lake/data"
metadata_path = "~/.dkdc/lake/metadata"

# Docker settings
container_name = "dkdc-postgres"
image = "postgres:latest"
restart_policy = "unless-stopped"

# Connection settings
max_startup_attempts = 30
startup_timeout_seconds = 15
"""


def init_config() -> None:
    """Initialize config file if it doesn't exist."""
    config_path = get_config_path()
    config_dir = config_path.parent

    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)

    # Create default config if it doesn't exist
    if not config_path.exists():
        config_path.write_text(get_default_config())


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    config_path = get_config_path()
    if not config_path.exists():
        init_config()

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def open_config() -> None:
    """Open config file in editor."""
    config_path = get_config_path()

    # Initialize config if it doesn't exist
    init_config()

    # Get editor from environment or default to vi
    editor = os.environ.get("EDITOR", "vi")

    typer.echo(f"Opening {config_path} with {editor}...")

    try:
        result = subprocess.run([editor, str(config_path)], check=True)
        if result.returncode != 0:
            typer.echo(f"Editor exited with status {result.returncode}", err=True)
            raise typer.Exit(1)
    except FileNotFoundError:
        typer.echo(f"Editor '{editor}' not found in PATH", err=True)
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        typer.echo(f"Editor exited with non-zero status: {e.returncode}", err=True)
        raise typer.Exit(1)
