#!/usr/bin/env python3
"""Parse all packaged Python sources without creating bytecode."""
from __future__ import annotations

import ast
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
files = sorted((ROOT / "src").rglob("*.py"))
files += sorted((ROOT / "tests").rglob("*.py"))
files += sorted((ROOT / "validation").glob("*.py"))
files += sorted((ROOT / "analysis").glob("*.py"))
for path in files:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
print(json.dumps({"schema": "rrct.v056.syntax_verification.v1", "status": "PASSED", "files_parsed": len(files)}, sort_keys=True))
