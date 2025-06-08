"""Configuration constants for dkdc."""

from pathlib import Path

# Database connection configuration
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "dkdc"
POSTGRES_USER = "dkdc"
POSTGRES_PASSWORD = "dkdc"
POSTGRES_CONTAINER_NAME = "dkdc-dl-metadata"

# Connection timeouts and retries
MAX_POSTGRES_STARTUP_ATTEMPTS = 30
POSTGRES_STARTUP_TIMEOUT_MSG = "Postgres failed to become ready in 15 seconds"

# File system paths
POSTGRES_DATA_PATH = Path.home() / "lake" / "data"
POSTGRES_DATA_DIR = Path.home() / "lake" / "metadata"

# Schema configuration
METADATA_SCHEMAS = ["dev", "stage", "prod"]
DEFAULT_METADATA_SCHEMA = METADATA_SCHEMAS[0]  # "dev"

# Docker configuration
DOCKER_POSTGRES_IMAGE = "postgres:latest"
DOCKER_RESTART_POLICY = "unless-stopped"

# Environment variables
ENV_DEFAULT_METADATA_SCHEMA = "DKDC_DL_DEFAULT_METADATA_SCHEMA"

# Table names
SECRETS_TABLE_NAME = "secrets"
FILES_TABLE_NAME = "files"

# Backup configuration
BACKUP_FILENAME_TEMPLATE = "backup_directory_{name}.zip"

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
DOCKER_INSTALL_URL = "https://docs.docker.com/desktop/setup/install/mac-install"

# SQL extensions
DUCKLAKE_EXTENSION = "ducklake"
POSTGRES_EXTENSION = "postgres"

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
