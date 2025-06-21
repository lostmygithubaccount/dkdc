"""Configuration constants for dkdc."""

from pathlib import Path

# Database configuration
SQLITE_METADATA_PATH = Path.home() / "lake" / "metadata.db"
DATA_PATH = Path.home() / "lake" / "data"
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
