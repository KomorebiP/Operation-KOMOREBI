#!/usr/bin/env python3
"""Verify the delivered files against SHA256SUMS.txt using the standard library."""
from pathlib import Path
import hashlib


def main() -> None:
    root = Path(__file__).resolve().parent
    manifest = root / 'SHA256SUMS.txt'
    if not manifest.is_file():
        raise SystemExit('SHA256SUMS.txt is missing.')
    failures: list[str] = []
    checked = 0
    for line in manifest.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        digest, name = line.split('  ', 1)
        target = (root / name).resolve()
        if not target.is_relative_to(root) or not target.is_file():
            failures.append(f'Missing or unsafe path: {name}')
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        checked += 1
        if actual != digest:
            failures.append(f'Checksum mismatch: {name}')
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f'All {checked} recorded file checksums match.')


if __name__ == '__main__':
    main()
