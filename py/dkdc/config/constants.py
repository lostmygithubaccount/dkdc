"""Configuration constants for dkdc."""

import shutil
from pathlib import Path

import typer


# DKDC directory path
def get_dkdc_dir() -> Path:
    """Get the path to the dkdc directory."""
    return Path.home() / ".dkdc"


def migrate_legacy_lake_directory() -> None:
    """Migrate legacy lake directories to ~/.dkdc/dkdclake if they exist.

    Handles migration from:
    1. ~/lake -> ~/.dkdc/dkdclake (original location)
    2. ~/.dkdc/lake -> ~/.dkdc/dkdclake (intermediate location)

    TODO: Remove this migration code on major version bump (v1.0.0+)
    """
    # Define possible legacy paths in order of priority
    legacy_paths = [
        Path.home() / "lake",  # Original location
        get_dkdc_dir() / "lake",  # Intermediate location
    ]

    new_dkdc_dir = get_dkdc_dir()
    new_lake_path = new_dkdc_dir / "dkdclake"

    # Find the first existing legacy path
    for legacy_path in legacy_paths:
        if legacy_path.exists() and not new_lake_path.exists():
            typer.echo(
                f"🔄 Migrating data from {legacy_path} to {new_lake_path}...",
                color="yellow",
            )

            # Ensure the new directory structure exists
            new_dkdc_dir.mkdir(parents=True, exist_ok=True)

            # Move the entire lake directory
            shutil.move(str(legacy_path), str(new_lake_path))

            typer.echo(
                f"✅ Successfully migrated data to {new_lake_path}", color="green"
            )
            break  # Only migrate from the first found legacy path


# Database configuration
SQLITE_METADATA_PATH = get_dkdc_dir() / "dkdclake" / "metadata.db"
DATA_PATH = get_dkdc_dir() / "dkdclake" / "data"
METADATA_DB_NAME = "metadata"
DATA_DB_NAME = "data"

# Table names
SECRETS_TABLE_NAME = "secrets"
FILES_TABLE_NAME = "files"
ARCHIVES_TABLE_NAME = "archives"

# Backup configuration
ARCHIVE_FILENAME_TEMPLATE = "archive_directory_{name}.zip"

# CLI color theme
COLORS = {
    "primary": "#8b5cf6",  # violet
    "secondary": "#06b6d4",  # cyan
    "success": "#10b981",  # emerald
    "warning": "#f59e0b",  # amber
    "error": "#ef4444",  # red
    "muted": "#6b7280",  # gray
    "accent": "#a855f7",  # purple
}

# Ibis default configuration
IBIS_INTERACTIVE = True
IBIS_MAX_ROWS = 40
IBIS_MAX_COLUMNS = None

# Installation URLs
DUCKDB_INSTALL_URL = "curl https://install.duckdb.org | sh"

# SQL extensions
DUCKLAKE_EXTENSION = "ducklake"
SQLITE_EXTENSION = "sqlite"

# ASCII art banner
DKDC_BANNER = r"""
▓█████▄  ██ ▄█▀▓█████▄  ▄████▄  
▒██▀ ██▌ ██▄█▒ ▒██▀ ██▌▒██▀ ▀█  
░██   █▌▓███▄░ ░██   █▌▒▓█    ▄ 
░▓█▄   ▌▓██ █▄ ░▓█▄   ▌▒▓▓▄ ▄██▒
░▒████▓ ▒██▒ █▄░▒████▓ ▒ ▓███▀ ░
 ▒▒▓  ▒ ▒ ▒▒ ▓▒ ▒▒▓  ▒ ░ ░▒ ▒  ░
 ░ ▒  ▒ ░ ░▒ ▒░ ░ ▒  ▒   ░  ▒   
 ░ ░  ░ ░ ░░ ░  ░ ░  ░ ░        
   ░    ░  ░      ░    ░ ░      
 ░              ░      ░

develop knowledge, develop code
"""

# we'll switch to this once we hit v1.0.0, then use above for dev builds and such
"""
██████╗ ██╗  ██╗██████╗  ██████╗
██╔══██╗██║ ██╔╝██╔══██╗██╔════╝
██║  ██║█████╔╝ ██║  ██║██║     
██║  ██║██╔═██╗ ██║  ██║██║     
██████╔╝██║  ██╗██████╔╝╚██████╗
╚═════╝ ╚═╝  ╚═╝╚═════╝  ╚═════╝

develop knowledge, develop code
"""
