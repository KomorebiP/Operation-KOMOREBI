#!/usr/bin/env python3
"""Static checker CLI for OSL-Core 0.3."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

try:  # pragma: no cover
    from .osl_model import OSLError
    from .osl_parser import parse_and_check
except ImportError:  # pragma: no cover
    from osl_model import OSLError  # type: ignore
    from osl_parser import parse_and_check  # type: ignore


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Statically check an OSL-Core 0.3 program")
    parser.add_argument("program", type=Path)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        statements, report = parse_and_check(args.program.read_text(encoding="utf-8"))
    except OSLError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2, sort_keys=True))
        return 1
    print(
        json.dumps(
            {
                "ok": True,
                "statement_count": len(statements),
                "report": {
                    "statement_count": report.statement_count,
                    "symbol_counts": report.symbol_counts,
                    "warnings": list(report.warnings),
                    "report_digest": report.report_digest,
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
