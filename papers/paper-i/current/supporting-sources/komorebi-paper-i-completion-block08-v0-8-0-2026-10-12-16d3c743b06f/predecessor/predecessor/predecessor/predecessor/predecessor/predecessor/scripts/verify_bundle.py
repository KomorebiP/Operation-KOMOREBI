#!/usr/bin/env python3
"""Verify an unpacked handoff against its SHA-256 manifest, including extra files.
Usage: python3 scripts/verify_bundle.py /path/to/package-root
This checks file integrity, not the truth of the mathematical claims.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def verify(root: Path) -> int:
    root = root.resolve(strict=True)
    manifest = json.loads((root / 'MANIFEST_SHA256.json').read_text())
    rows = manifest['files']
    if len(rows) != manifest['count']:
        raise ValueError('Manifest count mismatch')
    expected: set[str] = set()
    for row in rows:
        rel = PurePosixPath(row['path'])
        if rel.is_absolute() or '..' in rel.parts or str(rel) in expected:
            raise ValueError('Unsafe or duplicate manifest path')
        expected.add(str(rel))
        path = root / str(rel)
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise ValueError(f'Missing, linked or invalid file: {rel}')
        if path.stat().st_size != row['bytes'] or digest(path) != row['sha256']:
            raise ValueError(f'Integrity mismatch: {rel}')
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    if actual != expected | {'MANIFEST_SHA256.json'}:
        raise ValueError('Unlisted or missing payload files')
    print(json.dumps({'status': 'PASS', 'payload_files': len(rows),
                      'scope': 'File integrity only; mathematical receipts remain separate'}))
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    try:
        sys.exit(verify(args.root))
    except (OSError, KeyError, ValueError, TypeError) as error:
        print(f'BUNDLE VERIFICATION FAILED: {error}', file=sys.stderr)
        sys.exit(1)
