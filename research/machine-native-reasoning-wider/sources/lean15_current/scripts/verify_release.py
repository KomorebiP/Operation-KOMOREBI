#!/usr/bin/env python3
"""Check the frozen release bytes. This is integrity verification, not Lean compilation."""
from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    manifest=ROOT/'SHA256SUMS.json'
    if not manifest.is_file():
        print('No frozen SHA256SUMS.json is present.',file=sys.stderr);return 1
    data=json.loads(manifest.read_text()); failures=[]
    actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
            if p.is_file() and p.name!='SHA256SUMS.json' and '__pycache__' not in p.parts}
    extra=actual-set(data['files'])
    if extra: failures.extend(f'Unlisted payload file: {p}' for p in sorted(extra))
    for rel,expected in data['files'].items():
        name=Path(rel)
        if name.is_absolute() or '..' in name.parts:
            failures.append(f'Unsafe manifest path: {rel}');continue
        path=ROOT/name
        if not path.is_file() or path.is_symlink():
            failures.append(f'Missing or symbolic file: {rel}');continue
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(4<<20),b''):h.update(block)
        if path.stat().st_size!=expected['bytes'] or h.hexdigest()!=expected['sha256']:
            failures.append(f'Changed file: {rel}')
    if failures:
        print('\n'.join(failures),file=sys.stderr);return 1
    print(f'PASS: {len(data["files"])} payload files match the frozen release inventory.')
    print('This confirms byte integrity, not theorem validity or source authenticity.')
    return 0
if __name__=='__main__':raise SystemExit(main())
