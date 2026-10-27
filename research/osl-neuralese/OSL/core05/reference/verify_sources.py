#!/usr/bin/env python3
"""Parse every packaged Python source file without creating bytecode."""
from __future__ import annotations

import ast
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    files = sorted((root / "reference").glob("*.py")) + sorted((root / "tests").glob("*.py"))
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print(f"AST_PARSE_PASS files={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
