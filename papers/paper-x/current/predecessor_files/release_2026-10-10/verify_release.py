#!/usr/bin/env python3
"""Verify the frozen Paper X delivery by SHA-256. This does not run proofs or tests."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path, PurePosixPath

def verify(root: Path, strict: bool = False) -> dict:
    root = root.resolve()
    manifest = json.loads((root / 'MANIFEST.json').read_text(encoding='utf-8'))
    errors = []
    expected = set()
    total_bytes = 0
    for entry in manifest['files']:
        name = entry['path']
        rel = PurePosixPath(name)
        if rel.is_absolute() or '..' in rel.parts or '\\' in name or name in expected:
            errors.append({'path': name, 'error': 'unsafe_or_duplicate_manifest_path'})
            continue
        expected.add(name)
        target = root.joinpath(*rel.parts)
        if not target.resolve().is_relative_to(root) or not target.is_file() or target.is_symlink():
            errors.append({'path': name, 'error': 'missing_or_nonregular_file'})
            continue
        data = target.read_bytes()
        total_bytes += len(data)
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            errors.append({'path': name, 'error': 'size_or_hash_mismatch'})
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    extras = sorted(actual - expected - {'MANIFEST.json'})
    if strict and extras:
        errors.append({'error': 'additional_files', 'paths': extras})
    return {'status': 'passed' if not errors else 'failed', 'manifest_files': len(manifest['files']),
            'bytes_read': total_bytes, 'errors': errors, 'additional_files': extras,
            'scope': 'file integrity only; no Lean compilation or scientific test execution'}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--strict', action='store_true', help='Also reject additional files.')
    args = parser.parse_args()
    try:
        result = verify(args.root, args.strict)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {'status': 'failed', 'error': f'{type(exc).__name__}: {exc}'}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'passed' else 1

if __name__ == '__main__':
    sys.exit(main())
