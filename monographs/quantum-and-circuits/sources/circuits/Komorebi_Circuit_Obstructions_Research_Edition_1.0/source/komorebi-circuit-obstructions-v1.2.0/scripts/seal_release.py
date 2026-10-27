#!/usr/bin/env python3
"""Explicitly snapshot release bytes. Sealing does not validate mathematics."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Explicitly authorize writing a byte seal')
    parser.add_argument('--evidence', action='store_true', help='Seal closure evidence instead of source inputs')
    args = parser.parse_args()
    if not args.write:
        parser.error('Use --write to request an explicit byte snapshot. This is not a test run.')
    index = json.loads((ROOT / 'archive/INDEX.json').read_text(encoding='utf-8'))
    for entry in index['checkpoints']:
        path = ROOT / entry['file']
        if sha(path) != entry['sha256']:
            raise ValueError('Historical archive changed: ' + entry['file'])
    files = {}
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file() or any(x in path.relative_to(ROOT).parts for x in ('build', '.git', '.lake', '__pycache__')):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if args.evidence:
            include = rel.startswith('evidence/closure/')
        else:
            include = (not rel.startswith('evidence/closure/') and
                       rel not in ('integrity/SOURCE_SEAL.json', 'integrity/EVIDENCE_SEAL.json'))
        if include:
            files[rel] = sha(path)
    name = 'EVIDENCE_SEAL.json' if args.evidence else 'SOURCE_SEAL.json'
    payload = {'scope': 'Closure evidence bytes' if args.evidence else 'Source, baseline, and archive bytes',
               'warning': 'Byte integrity only. Not a theorem certificate, signature, or novelty claim.',
               'files': files}
    (ROOT / 'integrity' / name).write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(f'Wrote {name}: {len(files)} files. Re-run scientific verification after source edits.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
