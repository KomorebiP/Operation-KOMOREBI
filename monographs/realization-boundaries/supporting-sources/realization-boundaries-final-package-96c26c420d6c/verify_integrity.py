#!/usr/bin/env python3
"""Verify the delivered snapshot against SHA256SUMS.txt (before rebuilding)."""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys


def main() -> int:
    root = Path(__file__).resolve().parent
    manifest = root / 'SHA256SUMS.txt'
    if not manifest.is_file():
        print('FAIL: SHA256SUMS.txt is missing.', file=sys.stderr)
        return 1
    checked = 0
    failures: list[str] = []
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        expected, relative = line.split('  ', 1)
        path = (root / relative).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            failures.append(f'Missing or invalid path: {relative}')
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f'Hash mismatch: {relative}')
        checked += 1
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        return 1
    print(f'PASS: {checked} delivered files match their SHA-256 hashes.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
