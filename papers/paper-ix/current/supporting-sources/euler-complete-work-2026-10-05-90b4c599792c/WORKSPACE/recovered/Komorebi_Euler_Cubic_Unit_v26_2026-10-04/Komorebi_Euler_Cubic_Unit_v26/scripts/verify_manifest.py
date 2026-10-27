#!/usr/bin/env python3
"""Read-only SHA-256 verification of the source release; not a proof checker."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

def main() -> int:
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'SHA256_MANIFEST.json').read_text())
    bad=[]
    for rel,digest in manifest['files'].items():
        p=root/rel
        if not p.is_file(): bad.append({'path':rel,'problem':'missing'})
        elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            bad.append({'path':rel,'problem':'hash mismatch'})
    print(json.dumps({'status':'PASS' if not bad else 'FAIL',
                      'verified_entries':len(manifest['files']), 'mismatches':bad},indent=2))
    return bool(bad)

if __name__=='__main__':
    sys.exit(main())
