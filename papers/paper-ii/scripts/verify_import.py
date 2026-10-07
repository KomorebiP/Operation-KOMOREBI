#!/usr/bin/env python3
"""Verify imported artifact bytes; this does not compile Lean or prove mathematics."""
from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parents[1]
record = json.loads((root / "provenance/GITHUB_IMPORT.json").read_text())
failures = []
for item in record["entries"]:
    path = root / item["destination"]
    if not path.is_file():
        failures.append({"path": item["destination"], "problem": "missing"})
    elif path.stat().st_size != item["bytes"] or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
        failures.append({"path": item["destination"], "problem": "bytes differ"})
for item in record["omitted_entries"]:
    if (root / item["path"]).exists():
        failures.append({"path": item["path"], "problem": "excluded artifact appeared"})
print(json.dumps({"status": "FAIL" if failures else "PASS", "files_checked": len(record["entries"]), "failures": failures, "scope": "imported file identity only; no new compiler or mathematical replay"}, indent=2))
sys.exit(bool(failures))
