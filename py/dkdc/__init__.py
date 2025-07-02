"""dkdc - don't know, don't care."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("dkdc")
except importlib.metadata.PackageNotFoundError:
    # Fallback for development
    try:
        with open("VERSION", "r") as f:
            __version__ = f.read().strip()
    except FileNotFoundError:
        __version__ = "0.0.0+dev"
