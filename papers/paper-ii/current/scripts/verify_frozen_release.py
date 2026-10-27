#!/usr/bin/env python3
"""Verify the frozen file set and preserved baseline; this is not a proof checker."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

def safe_path(value):
    if not isinstance(value, str) or not value or '\\' in value or ':' in value:
        raise ValueError('Invalid manifest path')
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts or '.' in p.parts or p.as_posix() != value:
        raise ValueError('Noncanonical manifest path: ' + value)
    return ROOT.joinpath(*p.parts)

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    manifest = json.loads((ROOT / 'MANIFEST_SHA256.json').read_text())
    items = manifest['files']
    paths = [item['path'] for item in items]
    if len(paths) != len(set(paths)) or manifest['count'] != len(items):
        raise ValueError('Duplicate path or inconsistent manifest count')
    if manifest['self_excluded'] != 'MANIFEST_SHA256.json' or 'MANIFEST_SHA256.json' in paths:
        raise ValueError('Invalid self exclusion')
    actual = set()
    for p in ROOT.rglob('*'):
        if p.is_symlink():
            raise ValueError('Symlink not permitted: ' + str(p.relative_to(ROOT)))
        if p.is_file():
            actual.add(p.relative_to(ROOT).as_posix())
    expected = set(paths) | {'MANIFEST_SHA256.json'}
    if actual != expected:
        raise ValueError('File set mismatch; missing=' + repr(sorted(expected - actual)) + '; extra=' + repr(sorted(actual - expected)))
    for item in items:
        p = safe_path(item['path'])
        if not p.is_file() or p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
            raise ValueError('File identity mismatch: ' + item['path'])
    baseline = json.loads((ROOT / 'verification/freeze_2026-10-20/BASELINE_PRESERVATION.json').read_text())
    originals = [item['original_path'] for item in baseline['files']]
    destinations = [item['preserved_path'] for item in baseline['files']]
    if len(originals) != len(set(originals)) or len(originals) != baseline['count']:
        raise ValueError('Baseline preservation inventory is inconsistent')
    if len(destinations) != len(set(destinations)):
        raise ValueError('Baseline preservation destinations are not unique')
    changed = set(baseline['changed_administrative_paths'])
    for item in baseline['files']:
        safe_path(item['original_path'])
        expected_path = ('verification/freeze_2026-10-20/before/' if item['original_path'] in changed else '') + item['original_path']
        if item['preserved_path'] != expected_path:
            raise ValueError('Invalid baseline preservation mapping: ' + item['original_path'])
        p = safe_path(item['preserved_path'])
        if not p.is_file() or p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
            raise ValueError('Preserved baseline mismatch: ' + item['original_path'])
    print('Integrity PASS: ' + str(len(items)) + ' listed files, exact file set, all sizes and SHA-256 values match.')
    print('Baseline preservation PASS: ' + str(len(originals)) + ' original files retained with identical bytes.')
    print('This checks file identity and preservation, not mathematical correctness or a fresh Lean run.')

if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Integrity FAILED: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
