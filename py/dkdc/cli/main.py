"""dkdc CLI - thin wrapper around Rust CLI."""

import sys


def main():
    """Main CLI entry point - passes through to Rust CLI."""
    try:
        # Try to import the Rust extension
        from dkdc import _dkdc

        # Pass all arguments except the program name to the Rust CLI
        exit_code = _dkdc.run_cli(sys.argv[1:])
        sys.exit(exit_code)
    except ImportError:
        # Rust extension not built yet
        print("Error: dkdc is not properly installed.", file=sys.stderr)
        print("", file=sys.stderr)
        print("For development:", file=sys.stderr)
        print("  uv run maturin develop", file=sys.stderr)
        print("", file=sys.stderr)
        print("For installation:", file=sys.stderr)
        print("  uv tool install dkdc", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
