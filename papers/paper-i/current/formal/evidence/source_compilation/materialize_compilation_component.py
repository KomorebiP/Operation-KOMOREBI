#!/usr/bin/env python3
"""Restore the original evidence layout into a new directory, without running Lean."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_path(value):
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError(f'Invalid relative path: {value}')
    return Path(*path.parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', nargs='?', type=Path, help='New directory for the original layout')
    parser.add_argument('--check-only', action='store_true', help='Validate all locations without copying')
    args = parser.parse_args()
    if args.check_only == (args.destination is not None):
        parser.error('Provide either a new destination or --check-only')
    component = Path(__file__).resolve().parent
    root = component.parents[2]
    closure = root / 'formal/evidence/whole_closure'
    mapping = json.loads((component / 'OBJECT_LOCATIONS.json').read_text())
    if sha(component / 'verification.json') != mapping['component_receipt_sha256']:
        raise ValueError('Component receipt hash mismatch')
    if sha(closure / 'verification.json') != mapping['whole_closure_receipt_sha256']:
        raise ValueError('Whole-closure receipt hash mismatch')
    original = json.loads((component / 'verification.json').read_text())
    final = json.loads((closure / 'verification.json').read_text())
    expected = {r['object']: r['object_sha256'] for r in original['modules']}
    expected['objects/ReleaseBoundary.olean'] = original['boundary_compilation_component']['object_sha256']
    canonical = {r['object']: r['object_sha256'] for r in final['source_files']}
    canonical['objects/ReleaseBoundary.olean'] = final['boundary']['object_sha256']
    rows = mapping['objects']
    if len(rows) != 116 or mapping['object_count'] != len(rows):
        raise ValueError('Unexpected object count')
    if len({r['original_path'] for r in rows}) != len(rows) or {r['original_path'] for r in rows} != set(expected):
        raise ValueError('Locations do not exactly cover the original receipt')
    checked = []
    for row in rows:
        old = relative_path(row['original_path'])
        new = relative_path(row['canonical_release_path'])
        source = root / new
        if new != Path('formal/evidence/whole_closure') / old:
            raise ValueError('Unexpected canonical location')
        if source.is_symlink() or source.resolve() != source or not source.is_file():
            raise ValueError(f'Invalid canonical file: {source}')
        digest = row['sha256']
        if digest != expected[row['original_path']] or digest != canonical[row['original_path']]:
            raise ValueError('Object hash differs from an original receipt')
        if sha(source) != digest or source.stat().st_size != row['bytes']:
            raise ValueError(f'Object content mismatch: {source}')
        checked.append((old, source, digest))
    if args.destination is not None:
        destination = args.destination.resolve()
        if destination.exists() or destination.is_relative_to(root):
            parser.error('Destination must be a new directory outside the release tree')
        shutil.copytree(component, destination)
        for old, source, digest in checked:
            target = destination / old
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if sha(target) != digest:
                raise ValueError(f'Restored object hash mismatch: {target}')
        print(f'PASS: restored {len(checked)} objects to {destination}')
    else:
        print(f'PASS: validated {len(checked)} receipt-bound object locations')


if __name__ == '__main__':
    main()
