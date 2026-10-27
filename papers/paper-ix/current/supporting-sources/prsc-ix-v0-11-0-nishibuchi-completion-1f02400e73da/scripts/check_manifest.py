#!/usr/bin/env python3
"""Check the delivered file snapshot. Author: Komorebi P."""
from pathlib import Path
import hashlib
import json
import sys

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    try:
        manifest = json.loads((root / "MANIFEST.json").read_text())
        failures = []
        for relative, expected in manifest["files"].items():
            path = (root / relative).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                failures.append(relative + ": missing or unsafe path")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                failures.append(relative + ": SHA-256 mismatch")
        if failures:
            print("\n".join(failures), file=sys.stderr)
            return 1
        print(f"PASS: {len(manifest['files'])} manifested file hashes match")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Manifest check failed: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
