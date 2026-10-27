#!/usr/bin/env python3
"""Verify the delivered file inventory before build/report regeneration."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text())
    expected=set(manifest['files'])|{'MANIFEST.json'}
    actual={str(p.relative_to(ROOT)).replace('\\','/') for p in ROOT.rglob('*') if p.is_file()}
    if actual != expected:
        raise SystemExit(f'FAIL inventory: missing={sorted(expected-actual)}, extra={sorted(actual-expected)}; run this before generating files')
    for name,rec in manifest['files'].items():
        p=ROOT/name
        if p.is_absolute() and ROOT not in p.resolve().parents:
            raise SystemExit('FAIL: path outside project')
        if p.stat().st_size != rec['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=rec['sha256']:
            raise SystemExit(f'FAIL: changed {name}')
    print(f'PASS: {len(manifest["files"])} declared hashes and {len(actual)}-file inventory')

if __name__=='__main__': main()
