#!/usr/bin/env python3
"""Check the exact bytes named by this release's SHA-256 ledger."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parent
    ledger = json.loads((root / 'SHA256SUMS.json').read_text(encoding='utf-8'))
    failures = []
    for name, expected in ledger['files'].items():
        relative = Path(name)
        path = (root / relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not path.is_relative_to(root):
            failures.append(f'Unsafe ledger path: {name}')
            continue
        if not path.is_file():
            failures.append(f'Missing: {name}')
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f'Changed: {name}')
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        return 1
    print(f"PASS: {len(ledger['files'])} file hashes match. This is an integrity check, not a proof check.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
