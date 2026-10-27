"""Check the untouched delivery snapshot against its SHA-256 manifest.

The manifest is an integrity record, not a cryptographic authenticity signature.
Generated reports may change when tests are rerun. Verify before rerunning them.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import sys


def verify(root: Path) -> list[str]:
    root = root.resolve()
    manifest = json.loads((root / 'MANIFEST_SHA256.json').read_text(encoding='utf-8'))
    failures = []
    for relative, record in manifest['files'].items():
        path = (root / relative).resolve()
        if root not in path.parents:
            failures.append(f'Unsafe manifest path: {relative}')
            continue
        if not path.is_file():
            failures.append(f'Missing file: {relative}')
            continue
        data = path.read_bytes()
        if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
            failures.append(f'Changed file: {relative}')
    return failures


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    try:
        failures = verify(root)
    except (OSError, KeyError, ValueError) as exc:
        print(f'Manifest verification failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        raise SystemExit(1)
    print('PASS: every manifest-listed delivery file matches its SHA-256 digest.')
