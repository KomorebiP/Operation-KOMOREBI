#!/usr/bin/env python3
"""Emit the compact integrated OSL-Core 0.3 closure certificate."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

try:  # pragma: no cover
    from .osl_formal_kernel import explore_kernel
except ImportError:  # pragma: no cover
    from osl_formal_kernel import explore_kernel  # type: ignore


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    certificate = explore_kernel()
    text = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    if args.json or args.output is None:
        print(text, end="")
    return 0 if certificate["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
