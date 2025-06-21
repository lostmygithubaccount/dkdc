#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typer",
#     "rich",
#     "dkdc",
# ]
#
# [tool.uv.sources]
# dkdc = { path = "../", editable = true }
# ///
"""Backup and restore dkdc metadata with triple encryption."""

from __future__ import annotations

import argparse
import getpass
import os
import socket
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rich.console import Console

# Add parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from py.dkdc.cli.utils import ensure_postgres_with_feedback
from py.dkdc.config.constants import (
    POSTGRES_CONTAINER_NAME,
    POSTGRES_DB,
    POSTGRES_USER,
)

console = Console()

# Configuration
BUCKET = "gs://dkdc-dl"
LAKE_DATA_DIR = Path.home() / "lake" / "data"
NUM_PASSPHRASES = 3  # Number of encryption layers (max 26 for A-Z)


def get_passphrase_letter(index: int) -> str:
    """Get passphrase letter (A-Z) for given index."""
    if index >= 26:
        raise ValueError(f"Passphrase index {index} exceeds maximum of 25 (A-Z)")
    return chr(ord("A") + index)


def check_hostname() -> None:
    """Ensure script is run from correct hostname."""
    hostname = socket.gethostname()
    if not hostname.startswith("dkdcsot"):
        console.print(
            "[red]❌ This script must be run from hostname starting with 'dkdcsot'[/red]"
        )
        console.print(f"[red]Current hostname: {hostname}[/red]")
        sys.exit(1)
    console.print(f"[green]✅ Hostname confirmed: {hostname}[/green]")


def check_gcloud_auth() -> None:
    """Ensure gcloud is authenticated."""
    try:
        result = subprocess.run(
            [
                "gcloud",
                "auth",
                "list",
                "--filter=status:ACTIVE",
                "--format=value(account)",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        if not result.stdout.strip():
            console.print("[red]❌ Not logged into gcloud[/red]")
            console.print("[yellow]Please run: gcloud auth login[/yellow]")
            sys.exit(1)
        console.print("[green]✅ gcloud authentication confirmed[/green]")
    except subprocess.CalledProcessError:
        console.print("[red]❌ Failed to check gcloud authentication[/red]")
        sys.exit(1)


def get_passphrase(prompt: str, passphrase: str | None = None) -> str:
    """Get passphrase from flag or prompt user."""
    if passphrase is not None:
        return passphrase
    return getpass.getpass(prompt)


def encrypt_layer(data: bytes, passphrase: str) -> bytes:
    """Encrypt data with AES-256-CBC using PBKDF2."""
    # Generate random salt and IV
    salt = os.urandom(16)
    iv = os.urandom(16)

    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = kdf.derive(passphrase.encode())

    # Pad data to block size
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Encrypt data
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Return salt + iv + encrypted data
    return salt + iv + encrypted_data


def decrypt_layer(data: bytes, passphrase: str) -> bytes:
    """Decrypt data with AES-256-CBC using PBKDF2."""
    # Extract salt, IV, and encrypted data
    salt = data[:16]
    iv = data[16:32]
    encrypted_data = data[32:]

    # Derive key using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend(),
    )
    key = kdf.derive(passphrase.encode())

    # Decrypt data
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    # Remove padding
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()

    return data


def multi_encrypt(data: bytes, passphrases: list[str]) -> bytes:
    """Apply multiple layers of encryption using AES-256-CBC."""
    encrypted = data
    for passphrase in passphrases:
        encrypted = encrypt_layer(encrypted, passphrase)
    return encrypted


def multi_decrypt(data: bytes, passphrases: list[str]) -> bytes:
    """Decrypt multi-encrypted data (in reverse order)."""
    decrypted = data
    for passphrase in reversed(passphrases):
        decrypted = decrypt_layer(decrypted, passphrase)
    return decrypted


def collect_passphrases(
    provided_passphrases: dict[str, str | None], verify: bool = True
) -> list[str]:
    """Collect passphrases from provided values or prompt user."""
    passphrases = []

    for i in range(NUM_PASSPHRASES):
        letter = get_passphrase_letter(i)
        provided = provided_passphrases.get(f"passphrase{letter}")

        if provided is not None:
            passphrases.append(provided)
        else:
            passphrase = get_passphrase(f"Enter passphrase {letter}: ")
            if verify:
                passphrase_verify = get_passphrase(f"Verify passphrase {letter}: ")
                if passphrase != passphrase_verify:
                    console.print(f"[red]❌ Passphrase {letter} doesn't match[/red]")
                    sys.exit(1)
            passphrases.append(passphrase)

    return passphrases


def backup(**kwargs) -> None:
    """Create and upload encrypted backup."""
    check_hostname()
    check_gcloud_auth()

    # Ensure Postgres is running
    console.print("[yellow]🐘 Ensuring Postgres container is running...[/yellow]")
    ensure_postgres_with_feedback()

    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    encrypted_file = f"metadata_backup_{timestamp}.sql.enc"

    console.print("[yellow]📦 Creating metadata backup...[/yellow]")

    # Dump database
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                POSTGRES_CONTAINER_NAME,
                "pg_dump",
                "-U",
                POSTGRES_USER,
                "-d",
                POSTGRES_DB,
            ],
            capture_output=True,
            check=True,
        )
        dump_data = result.stdout
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Database dump failed: {e.stderr.decode()}[/red]")
        sys.exit(1)

    # Get passphrases
    encryption_type = "triple" if NUM_PASSPHRASES == 3 else f"{NUM_PASSPHRASES}-layer"
    console.print(f"[yellow]🔐 Setting up {encryption_type} encryption...[/yellow]")

    passphrases = collect_passphrases(kwargs, verify=True)

    # Encrypt data
    try:
        encrypted_data = multi_encrypt(dump_data, passphrases)
    except RuntimeError as e:
        console.print(f"[red]❌ Encryption failed: {e}[/red]")
        sys.exit(1)

    # Write encrypted file
    Path(encrypted_file).write_bytes(encrypted_data)
    console.print(f"[green]✅ Backup created and encrypted: {encrypted_file}[/green]")

    # Upload to cloud storage
    console.print("[yellow]☁️  Uploading to cloud storage...[/yellow]")
    try:
        subprocess.run(
            ["gsutil", "cp", encrypted_file, f"{BUCKET}/metadata/"],
            check=True,
            capture_output=True,
        )
        console.print(
            f"[green]✅ Metadata backup uploaded: {BUCKET}/metadata/{encrypted_file}[/green]"
        )
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Upload failed: {e.stderr.decode()}[/red]")
        sys.exit(1)
    finally:
        # Clean up local encrypted file
        Path(encrypted_file).unlink()

    # Sync data directory
    if LAKE_DATA_DIR.exists():
        console.print("[yellow]📂 Syncing data directory...[/yellow]")
        try:
            subprocess.run(
                [
                    "gsutil",
                    "-m",
                    "rsync",
                    "-r",
                    "-d",
                    f"{LAKE_DATA_DIR}/",
                    f"{BUCKET}/data/",
                ],
                check=True,
            )
            console.print(f"[green]✅ Data directory synced: {BUCKET}/data/[/green]")
        except subprocess.CalledProcessError:
            console.print("[red]❌ Data sync failed[/red]")
            sys.exit(1)
    else:
        console.print(f"[yellow]⚠️  Data directory not found: {LAKE_DATA_DIR}[/yellow]")

    console.print("[green]🎉 Backup and sync complete![/green]")


def restore(backup_path: str, **kwargs) -> None:
    """Restore database from encrypted backup."""
    check_hostname()

    # Download backup if it's a GCS path
    if backup_path.startswith("gs://"):
        check_gcloud_auth()
        console.print(f"[yellow]☁️  Downloading backup from {backup_path}...[/yellow]")
        local_backup = Path(tempfile.mktemp(suffix=".sql.enc"))
        try:
            subprocess.run(
                ["gsutil", "cp", backup_path, str(local_backup)],
                check=True,
                capture_output=True,
            )
            console.print("[green]✅ Backup downloaded[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ Download failed: {e.stderr.decode()}[/red]")
            sys.exit(1)
    else:
        local_backup = Path(backup_path)
        if not local_backup.exists():
            console.print(f"[red]❌ Backup file not found: {backup_path}[/red]")
            sys.exit(1)

    # Read encrypted data
    encrypted_data = local_backup.read_bytes()

    # Get passphrases
    encryption_type = "triple" if NUM_PASSPHRASES == 3 else f"{NUM_PASSPHRASES}"
    console.print(
        f"[yellow]🔐 Decrypting backup (requires all {encryption_type} passphrases)...[/yellow]"
    )
    passphrases = collect_passphrases(kwargs, verify=False)

    # Decrypt data
    try:
        decrypted_data = multi_decrypt(encrypted_data, passphrases)
    except (RuntimeError, ValueError) as e:
        console.print(f"[red]❌ Decryption failed: {e}[/red]")
        console.print(
            "[yellow]Note: Passphrases must be entered in the same order as during backup[/yellow]"
        )
        sys.exit(1)

    # Clean up downloaded file if from GCS
    if backup_path.startswith("gs://"):
        local_backup.unlink()

    # Ensure Postgres is running
    console.print("[yellow]🐘 Ensuring Postgres container is running...[/yellow]")
    ensure_postgres_with_feedback()

    # Restore database
    console.print("[yellow]🔄 Restoring database...[/yellow]")
    proc = subprocess.Popen(
        [
            "docker",
            "exec",
            "-i",
            POSTGRES_CONTAINER_NAME,
            "psql",
            "-U",
            POSTGRES_USER,
            "-d",
            POSTGRES_DB,
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = proc.communicate(decrypted_data)

    if proc.returncode != 0:
        console.print(f"[red]❌ Restore failed: {stderr.decode()}[/red]")
        sys.exit(1)

    console.print("[green]🎉 Database restored successfully![/green]")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Backup and restore dkdc metadata with {NUM_PASSPHRASES}-layer encryption"
    )
    parser.add_argument(
        "--restore",
        metavar="PATH",
        help="Restore from backup file (local path or gs:// URL)",
    )

    # Dynamically add passphrase arguments
    for i in range(NUM_PASSPHRASES):
        letter = get_passphrase_letter(i)
        parser.add_argument(
            f"--passphrase{letter}",
            help=f"Passphrase {letter} (avoids interactive prompt)",
        )

    args = parser.parse_args()

    # Convert args to kwargs dict for passphrases
    passphrase_kwargs = {}
    for i in range(NUM_PASSPHRASES):
        letter = get_passphrase_letter(i)
        attr_name = f"passphrase{letter}"
        if hasattr(args, attr_name):
            passphrase_kwargs[attr_name] = getattr(args, attr_name)

    if args.restore:
        restore(args.restore, **passphrase_kwargs)
    else:
        backup(**passphrase_kwargs)


if __name__ == "__main__":
    main()
