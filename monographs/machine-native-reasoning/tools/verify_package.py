#!/usr/bin/env python3
"""Check the immutable package's exact regular-file set, sizes, and SHA-256 hashes.

Run before making local build outputs. This verifies delivery integrity, not
mathematical truth, provenance of an external compiler, or Lean proof replay.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys

MANIFEST = 'MANIFEST.json'
SCHEMA = 'komorebi.source-package.sha256.v1'


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 << 20), b''):
            h.update(block)
    return h.hexdigest()


def member_name(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError('A manifest path must be a nonempty string')
    if '\\' in value or ':' in value or any(ord(c) < 32 for c in value):
        raise ValueError(f'Invalid path characters: {value!r}')
    p = PurePosixPath(value)
    if p.is_absolute() or any(c in ('', '.', '..') for c in value.split('/')):
        raise ValueError(f'Noncanonical relative path: {value!r}')
    if str(p) != value or value == MANIFEST:
        raise ValueError(f'Invalid payload path: {value!r}')
    return value


def verify(root: Path) -> dict[str, object]:
    root = root.resolve(strict=True)
    manifest_path = root / MANIFEST
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError('Missing regular manifest')
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or data.get('schema') != SCHEMA:
        raise ValueError('Unsupported manifest schema')
    entries = data.get('files')
    if not isinstance(entries, list) or not entries:
        raise ValueError('A nonempty file inventory is required')
    expected: dict[str, dict[str, object]] = {}
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'path', 'bytes', 'sha256'}:
            raise ValueError('Invalid inventory entry')
        name = member_name(entry['path'])
        if name in expected:
            raise ValueError(f'Duplicate inventory path: {name}')
        size, sha = entry['bytes'], entry['sha256']
        if type(size) is not int or size < 0:
            raise ValueError(f'Invalid byte length: {name}')
        if not isinstance(sha, str) or re.fullmatch('[0-9a-f]{64}', sha) is None:
            raise ValueError(f'Invalid SHA-256: {name}')
        expected[name] = entry
    actual: set[str] = set()
    for path in root.rglob('*'):
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f'Symlink is not a delivered regular file: {path}')
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f'Nonregular payload: {path}')
        name = path.relative_to(root).as_posix()
        if name != MANIFEST:
            member_name(name)
            actual.add(name)
    if actual != set(expected):
        raise ValueError(f'File set differs. Missing={sorted(set(expected)-actual)[:10]}; '
                         f'extra={sorted(actual-set(expected))[:10]}')
    total = 0
    for name, entry in expected.items():
        path = root / name
        if path.stat().st_size != entry['bytes'] or digest(path) != entry['sha256']:
            raise ValueError(f'Byte-length or SHA-256 mismatch: {name}')
        total += path.stat().st_size
    return {'status': 'PASS', 'payload_files': len(expected), 'payload_bytes': total,
            'manifest_sha256': digest(manifest_path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = verify(args.root)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    print('Exact file set and all byte-length/SHA-256 records agree. This is not a proof check.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
