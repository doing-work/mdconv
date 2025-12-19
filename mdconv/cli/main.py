"""CLI entry point."""

import sys
from pathlib import Path

from mdconv.cli.commands import main as cli_main


def main():
    """Entry point for CLI."""
    sys.exit(cli_main())


if __name__ == "__main__":
    main()

