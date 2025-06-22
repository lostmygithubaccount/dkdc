"""Backup and restore commands for dkdc."""

import getpass
import os
import socket
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

import fsspec
import typer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rich.console import Console
from rich.prompt import Confirm

from dkdc.cli.utils import (
    ensure_setup_with_feedback,
    print_error,
    print_info,
    print_warning,
    spinner_task,
)
from dkdc.config.constants import SQLITE_METADATA_PATH

console = Console()
backup_app = typer.Typer(
    name="backup",
    help="Backup and restore commands.",
    invoke_without_command=True,
    no_args_is_help=False,
)

# Configuration
BUCKET = "gs://dkdc-dl"
LAKE_DATA_DIR = Path.home() / "lake" / "data"

# Passphrase configuration with colors and static salts
PASSPHRASE_CONFIG = {
    "A": {"color": "bright_red", "salt": b"dkdcA"},
    "B": {"color": "bright_green", "salt": b"dkdcB"},
    "C": {"color": "bright_blue", "salt": b"dkdcC"},
}

NUM_PASSPHRASES = len(PASSPHRASE_CONFIG)
PASSPHRASE_LETTERS = list(PASSPHRASE_CONFIG.keys())


def get_passphrase_config(letter: str) -> dict:
    """Get passphrase configuration for given letter."""
    if letter not in PASSPHRASE_CONFIG:
        raise ValueError(f"Passphrase {letter} not configured")
    return PASSPHRASE_CONFIG[letter]


def get_passphrase_letter(index: int) -> str:
    """Get passphrase letter for given index."""
    if index >= len(PASSPHRASE_LETTERS):
        raise ValueError(
            f"Passphrase index {index} exceeds maximum of {len(PASSPHRASE_LETTERS) - 1}"
        )
    return PASSPHRASE_LETTERS[index]


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


def encrypt_layer(data: bytes, passphrase: str, static_salt: bytes) -> bytes:
    """Encrypt data with AES-256-CBC using PBKDF2 and static salt."""
    # Use static salt but random IV for each encryption
    iv = os.urandom(16)

    # Derive key using PBKDF2 with static salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=static_salt,
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

    # Return iv + encrypted data (salt is static and known)
    return iv + encrypted_data


def decrypt_layer(data: bytes, passphrase: str, static_salt: bytes) -> bytes:
    """Decrypt data with AES-256-CBC using PBKDF2 and static salt."""
    # Extract IV and encrypted data (salt is static)
    iv = data[:16]
    encrypted_data = data[16:]

    # Derive key using PBKDF2 with static salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=static_salt,
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


def multi_encrypt(data: bytes, passphrase_dict: dict[str, str]) -> bytes:
    """Apply multiple layers of encryption using AES-256-CBC with static salts."""
    encrypted = data
    for letter in PASSPHRASE_LETTERS:
        if letter in passphrase_dict:
            config = get_passphrase_config(letter)
            encrypted = encrypt_layer(
                encrypted, passphrase_dict[letter], config["salt"]
            )
    return encrypted


def multi_decrypt(data: bytes, passphrase_dict: dict[str, str]) -> bytes:
    """Decrypt multi-encrypted data (in reverse order)."""
    decrypted = data
    for letter in reversed(PASSPHRASE_LETTERS):
        if letter in passphrase_dict:
            config = get_passphrase_config(letter)
            decrypted = decrypt_layer(
                decrypted, passphrase_dict[letter], config["salt"]
            )
    return decrypted


def collect_passphrases(
    provided_passphrases: dict[str, str | None], verify: bool = True
) -> dict[str, str]:
    """Collect passphrases from provided values or prompt user with colors."""
    passphrases = {}

    for letter in PASSPHRASE_LETTERS:
        config = get_passphrase_config(letter)
        provided = provided_passphrases.get(letter)

        if provided is not None:
            passphrases[letter] = provided
        else:
            # Color-coded prompts
            color = config["color"]

            console.print(f"[{color}]🔐 Passphrase {letter}[/{color}]")
            passphrase = get_passphrase(
                f"\x1b[91mEnter passphrase {letter}: \x1b[0m"
                if letter == "A"
                else f"\x1b[92mEnter passphrase {letter}: \x1b[0m"
                if letter == "B"
                else f"\x1b[94mEnter passphrase {letter}: \x1b[0m"
            )
            if verify:
                passphrase_verify = get_passphrase(
                    f"\x1b[91mVerify passphrase {letter}: \x1b[0m"
                    if letter == "A"
                    else f"\x1b[92mVerify passphrase {letter}: \x1b[0m"
                    if letter == "B"
                    else f"\x1b[94mVerify passphrase {letter}: \x1b[0m"
                )
                if passphrase != passphrase_verify:
                    console.print(f"[red]❌ Passphrase {letter} doesn't match[/red]")
                    sys.exit(1)
            passphrases[letter] = passphrase

    return passphrases


def backup_func(passphrase_dict: dict[str, str]) -> None:
    """Create and upload encrypted backup."""
    # Ensure database is set up
    console.print("[yellow]🗃️ Setting up database...[/yellow]")
    ensure_setup_with_feedback()

    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    encrypted_file = f"metadata_backup_{timestamp}.db.enc"

    console.print("[yellow]📦 Creating metadata backup...[/yellow]")

    # Read SQLite database file
    try:
        if SQLITE_METADATA_PATH.exists():
            dump_data = SQLITE_METADATA_PATH.read_bytes()
        else:
            console.print(
                f"[red]❌ SQLite file not found: {SQLITE_METADATA_PATH}[/red]"
            )
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Database backup failed: {e}[/red]")
        sys.exit(1)

    # Encrypt data
    try:
        encrypted_data = multi_encrypt(dump_data, passphrase_dict)
    except RuntimeError as e:
        console.print(f"[red]❌ Encryption failed: {e}[/red]")
        sys.exit(1)

    # Write encrypted file
    Path(encrypted_file).write_bytes(encrypted_data)
    console.print(
        f"[green]✅ SQLite backup created and encrypted: {encrypted_file}[/green]"
    )

    # Upload to cloud storage
    console.print("[yellow]☁️  Uploading to cloud storage...[/yellow]")
    try:
        subprocess.run(
            ["gsutil", "cp", encrypted_file, f"{BUCKET}/metadata/"],
            check=True,
            capture_output=True,
        )
        console.print(
            f"[green]✅ SQLite backup uploaded: {BUCKET}/metadata/{encrypted_file}[/green]"
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


def restore_data_only() -> None:
    """Restore only data files from cloud storage."""
    console.print("[yellow]📂 Restoring data files from cloud storage...[/yellow]")
    try:
        # Ensure data directory exists
        LAKE_DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Sync data from cloud storage
        subprocess.run(
            [
                "gsutil",
                "-m",
                "rsync",
                "-r",
                "-d",
                f"{BUCKET}/data/",
                f"{LAKE_DATA_DIR}/",
            ],
            check=True,
            capture_output=True,
        )
        console.print(f"[green]✅ Data files restored to: {LAKE_DATA_DIR}[/green]")
        console.print("[green]🎉 Data restore complete![/green]")
    except subprocess.CalledProcessError as e:
        console.print(
            f"[red]❌ Data restore failed: {e.stderr.decode() if e.stderr else e}[/red]"
        )
        console.print(
            f"[yellow]💡 You can manually sync with: gsutil -m rsync -r -d {BUCKET}/data/ {LAKE_DATA_DIR}/[/yellow]"
        )
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Data restore failed: {e}[/red]")
        sys.exit(1)


def restore_func(
    backup_path: str, restore_data: bool = False, passphrase_dict: dict[str, str] = None
) -> None:
    """Restore SQLite database from encrypted backup."""
    if passphrase_dict is None:
        passphrase_dict = {}

    # Download backup if it's a GCS path
    if backup_path.startswith("gs://"):
        console.print(f"[yellow]☁️  Downloading backup from {backup_path}...[/yellow]")
        local_backup = Path(tempfile.mktemp(suffix=".db.enc"))
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

    # Decrypt data
    try:
        decrypted_data = multi_decrypt(encrypted_data, passphrase_dict)
    except (RuntimeError, ValueError) as e:
        console.print(f"[red]❌ Decryption failed: {e}[/red]")
        console.print(
            "[yellow]Note: Passphrases must be entered in the same order as during backup[/yellow]"
        )
        sys.exit(1)

    # Clean up downloaded file if from GCS
    if backup_path.startswith("gs://"):
        local_backup.unlink()

    # Ensure database directory exists
    console.print("[yellow]🗃️ Setting up database...[/yellow]")
    ensure_setup_with_feedback()

    # Restore database by writing to SQLite file
    console.print("[yellow]🔄 Restoring SQLite database...[/yellow]")
    try:
        # Backup existing file if it exists
        if SQLITE_METADATA_PATH.exists():
            backup_existing = SQLITE_METADATA_PATH.with_suffix(".db.backup")
            SQLITE_METADATA_PATH.rename(backup_existing)
            console.print(
                f"[yellow]📋 Existing database backed up to: {backup_existing}[/yellow]"
            )

        # Write restored data
        SQLITE_METADATA_PATH.write_bytes(decrypted_data)
        console.print("[green]🎉 SQLite database restored successfully![/green]")
    except Exception as e:
        console.print(f"[red]❌ Restore failed: {e}[/red]")
        sys.exit(1)

    # Restore data files if requested
    if restore_data:
        console.print("[yellow]📂 Restoring data files from cloud storage...[/yellow]")
        try:
            # Ensure data directory exists
            LAKE_DATA_DIR.mkdir(parents=True, exist_ok=True)

            # Sync data from cloud storage
            subprocess.run(
                [
                    "gsutil",
                    "-m",
                    "rsync",
                    "-r",
                    "-d",
                    f"{BUCKET}/data/",
                    f"{LAKE_DATA_DIR}/",
                ],
                check=True,
                capture_output=True,
            )
            console.print(f"[green]✅ Data files restored to: {LAKE_DATA_DIR}[/green]")
        except subprocess.CalledProcessError as e:
            console.print(
                f"[red]❌ Data restore failed: {e.stderr.decode() if e.stderr else e}[/red]"
            )
            console.print(
                "[yellow]💡 Metadata was restored successfully, but data files failed[/yellow]"
            )
            console.print(
                f"[yellow]💡 You can manually sync with: gsutil -m rsync -r -d {BUCKET}/data/ {LAKE_DATA_DIR}/[/yellow]"
            )
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]❌ Data restore failed: {e}[/red]")
            sys.exit(1)

    if restore_data:
        console.print("[green]🎉 Full restore complete (metadata + data)![/green]")
    else:
        console.print("[green]📋 Metadata restore complete![/green]")
        console.print(
            "[yellow]💡 To also restore data files, use: --restore-data[/yellow]"
        )


def list_backups() -> list[str]:
    """List available backup files from GCS, sorted by date (newest first)."""
    try:
        # Create GCS filesystem (auth should be handled by your setup)
        fs = fsspec.filesystem("gcs")

        # Use glob to find backup files
        bucket_path = BUCKET.removeprefix("gs://")
        pattern = f"{bucket_path}/metadata/metadata_backup_*.db.enc"

        files = fs.glob(pattern)

        if not files:
            return []

        # Add gs:// prefix and sort by filename (which contains timestamp)
        gcs_files = [f"gs://{f}" for f in files]
        return sorted(gcs_files, reverse=True)  # Newest first

    except Exception as e:
        print_error("Failed to list backups from GCS", str(e))
        raise typer.Exit(1)


def get_latest_backup() -> Optional[str]:
    """Get the latest backup file from GCS."""
    backups = list_backups()
    return backups[0] if backups else None


def extract_backup_date(backup_path: str) -> str:
    """Extract readable date from backup filename."""
    try:
        # Extract timestamp from filename like: metadata_backup_20241221_143022.db.enc
        filename = Path(backup_path).name
        timestamp_part = (
            filename.split("_")[2] + "_" + filename.split("_")[3].split(".")[0]
        )
        # Parse: 20241221_143022
        dt = datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return "unknown date"


@backup_app.callback()
def backup_main(
    restore: bool = typer.Option(
        False, "--restore", help="Restore metadata and data from latest backup"
    ),
    restore_file: Optional[str] = typer.Option(
        None, "--restore-file", help="Specific backup file to restore"
    ),
    metadata_only: bool = typer.Option(
        False, "--metadata-only", help="Restore only metadata (not data files)"
    ),
    restore_data_only: bool = typer.Option(
        False, "--restore-data", help="Restore only data files from cloud storage"
    ),
    list_backups_flag: bool = typer.Option(
        False, "--list", help="List available backups"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
    passphrase_a: Optional[str] = typer.Option(
        None, "--passphrase-a", help="Passphrase A"
    ),
    passphrase_b: Optional[str] = typer.Option(
        None, "--passphrase-b", help="Passphrase B"
    ),
    passphrase_c: Optional[str] = typer.Option(
        None, "--passphrase-c", help="Passphrase C"
    ),
) -> None:
    """Create triple-encrypted backups or restore from cloud storage."""

    # Check prerequisites (these functions have their own output)
    check_hostname()
    check_gcloud_auth()

    # Handle --list flag
    if list_backups_flag:
        with spinner_task("Searching for backups"):
            backups = list_backups()

        if not backups:
            console.print("[yellow]No backups found[/yellow]")
            return

        console.print(f"[cyan]Found {len(backups)} backup(s):[/cyan]")
        console.print()

        for i, backup in enumerate(backups):
            date_str = extract_backup_date(backup)
            filename = Path(backup).name
            if i == 0:
                console.print(
                    f"[bright_green]→[/bright_green] [bold]{filename}[/bold] [dim]({date_str})[/dim] [bright_green]← latest[/bright_green]"
                )
            else:
                console.print(f"  [bold]{filename}[/bold] [dim]({date_str})[/dim]")
        return

    # Handle --restore-data (standalone)
    if restore_data_only:
        if not yes:
            if not Confirm.ask(
                f"Restore data files to {LAKE_DATA_DIR}?", default=False
            ):
                print_warning("Data restore cancelled")
                raise typer.Exit(0)

        try:
            restore_data_only()
        except Exception as e:
            print_error("Data restore failed", str(e))
            raise typer.Exit(1)
        return

    # Handle --restore or --restore-file
    if restore or restore_file is not None:
        # Get backup file to restore
        if restore:  # --restore flag means use latest
            with spinner_task("Finding latest backup"):
                backup_file = get_latest_backup()
            if backup_file is None:
                print_error(
                    "No backups found", f"No backup files in {BUCKET}/metadata/"
                )
                raise typer.Exit(1)
            print_info("Using latest backup", f"{Path(backup_file).name}")
        else:  # --restore-file specified
            backup_file = restore_file
            # If user provided a filename, convert to full GCS path
            if not backup_file.startswith("gs://"):
                backup_file = f"{BUCKET}/metadata/{backup_file}"

        # Show what will be restored
        date_str = extract_backup_date(backup_file)
        restore_type = "metadata only" if metadata_only else "metadata + data files"

        print_info(
            "Restore plan", f"{restore_type} from {Path(backup_file).name} ({date_str})"
        )

        if not yes:
            if not Confirm.ask(f"Restore {restore_type}?", default=False):
                print_warning("Restore cancelled")
                raise typer.Exit(0)

        # Prepare passphrase dict
        provided_passphrases = {}
        if passphrase_a:
            provided_passphrases["A"] = passphrase_a
        if passphrase_b:
            provided_passphrases["B"] = passphrase_b
        if passphrase_c:
            provided_passphrases["C"] = passphrase_c

        # Get passphrases
        console.print(
            "[yellow]🔐 Decrypting backup (requires all 3 passphrases)...[/yellow]"
        )
        passphrases = collect_passphrases(provided_passphrases, verify=False)

        # Run restore (default is to restore both metadata and data)
        restore_data_flag = not metadata_only
        try:
            restore_func(
                backup_file, restore_data=restore_data_flag, passphrase_dict=passphrases
            )
        except Exception as e:
            print_error("Restore failed", str(e))
            raise typer.Exit(1)
        return

    # Default: Create backup (no confirmation needed - user explicitly asked for it)
    print_info(
        "Creating backup", "Triple-encrypted metadata + data sync to cloud storage"
    )

    # Prepare passphrase dict
    provided_passphrases = {}
    if passphrase_a:
        provided_passphrases["A"] = passphrase_a
    if passphrase_b:
        provided_passphrases["B"] = passphrase_b
    if passphrase_c:
        provided_passphrases["C"] = passphrase_c

    # Get passphrases
    console.print("[yellow]🔐 Setting up triple encryption...[/yellow]")
    passphrases = collect_passphrases(provided_passphrases, verify=True)

    # Run backup (backup function provides its own progress output)
    try:
        backup_func(passphrases)
    except Exception as e:
        print_error("Backup failed", str(e))
        raise typer.Exit(1)


# Add the backup app to main CLI
if __name__ == "__main__":
    backup_app()
