#!/usr/bin/env python3
"""Check the shipped source seal. Byte integrity is not mathematical verification."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify(root: Path = ROOT) -> dict:
    data = json.loads((root / 'integrity/SOURCE_SEAL.json').read_text(encoding='utf-8'))
    errors = []
    evidence_path = root / 'integrity/EVIDENCE_SEAL.json'
    evidence = json.loads(evidence_path.read_text(encoding='utf-8'))['files'] if evidence_path.is_file() else {}
    for relative, expected in {**data['files'], **evidence}.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            errors.append(f'path escape: {relative}')
        elif not path.is_file():
            errors.append(f'missing: {relative}')
        elif digest(path) != expected:
            errors.append(f'changed: {relative}')
    if errors:
        raise ValueError('; '.join(errors))
    return {'status': 'PASS', 'sealed_files': len(data['files']), 'sealed_evidence_files': len(evidence),
            'meaning': 'Shipped bytes match the source seal; not a proof certificate.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.root), indent=2))
        return 0
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
