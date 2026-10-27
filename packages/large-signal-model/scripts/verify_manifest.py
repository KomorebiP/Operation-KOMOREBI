"""Verify exact source files listed in RELEASE_MANIFEST.json, without network I/O.

New local results are ignored unless --strict is selected. Build-system-added
PKG-INFO and egg-info metadata in a standard sdist are reported as extras in
strict mode; they do not invalidate the hashes of declared source files.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main() -> int:
    parser=argparse.ArgumentParser();parser.add_argument('--strict',action='store_true')
    args=parser.parse_args()
    manifest=ROOT/'RELEASE_MANIFEST.json'
    data=json.loads(manifest.read_text(encoding='utf-8'))
    errors=[];declared=set()
    for row in data['files']:
        relative=Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts or str(relative) in declared:
            errors.append(f'invalid or duplicate path: {relative}');continue
        declared.add(relative.as_posix());path=ROOT/relative
        if not path.is_file(): errors.append(f'missing: {relative}');continue
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual!=row['sha256'] or path.stat().st_size!=row['bytes']:
            errors.append(f'content mismatch: {relative}')
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file()}
    extras=sorted(actual-declared-{'RELEASE_MANIFEST.json'})
    if args.strict and extras: errors.append('unlisted files present')
    report={'ok':not errors,'verified_files':len(declared),'strict':args.strict,
            'extra_files':extras,'errors':errors}
    print(json.dumps(report,indent=2))
    return 0 if not errors else 1


if __name__=='__main__': raise SystemExit(main())
