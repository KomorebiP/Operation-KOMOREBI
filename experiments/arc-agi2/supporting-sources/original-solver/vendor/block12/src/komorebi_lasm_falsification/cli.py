"""Command-line entry point for PR-LASM Block 12.

Author: Komorebi P.
"""
from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "audit"))
    args, remainder = parser.parse_known_args()
    import sys
    sys.argv = [sys.argv[0], *remainder]
    if args.command == "freeze":
        from .freeze import main as selected_main
    else:
        from .audit import main as selected_main
    return selected_main()


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
