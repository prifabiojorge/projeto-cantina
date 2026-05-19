#!/usr/bin/env python3
"""Root runner for the legacy local Cantina server."""

from pathlib import Path
import runpy


def main():
    runpy.run_path(str(Path(__file__).resolve().parent / "sistema_cantina" / "run.py"), run_name="__main__")


if __name__ == "__main__":
    main()
