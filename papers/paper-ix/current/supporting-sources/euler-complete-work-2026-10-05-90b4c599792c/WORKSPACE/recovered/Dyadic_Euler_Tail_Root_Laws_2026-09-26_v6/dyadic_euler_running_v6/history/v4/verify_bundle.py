#!/usr/bin/env python3
"""Verify retained release hashes. Run before regenerating scientific outputs."""
from pathlib import Path
import hashlib
import json


def main() -> None:
    base = Path(__file__).resolve().parent
    ledger = json.loads((base / 'SHA256SUMS.json').read_text(encoding='utf-8'))
    checked = 0
    for name, expected in ledger['sha256'].items():
        rel = Path(name)
        path = (base / rel).resolve()
        if rel.is_absolute() or '..' in rel.parts or not path.is_relative_to(base):
            raise ValueError(f'Unsafe ledger path: {name}')
        if not path.is_file():
            raise FileNotFoundError(f'Missing retained file: {name}')
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Hash mismatch: {name}')
        checked += 1
    print(f'PASS: {checked} retained file hashes. This verifies integrity, not mathematical truth.')


if __name__ == '__main__':
    main()
