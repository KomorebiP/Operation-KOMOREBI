#!/usr/bin/env python3
"""Verify all expected release files against the shipped SHA-256 manifest."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
manifest=json.loads((root/'RELEASE_MANIFEST.json').read_text(encoding='utf-8'))
failed=[]
for rel,expected in manifest['files'].items():
    p=root/rel
    if not p.is_file():
        failed.append((rel,'missing'))
        continue
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    if p.stat().st_size!=expected['bytes'] or h.hexdigest()!=expected['sha256']:
        failed.append((rel,'content mismatch'))
if failed:
    for rel,reason in failed:print('FAIL',rel,reason)
    sys.exit(1)
print('PASS:',len(manifest['files']),'release files match their SHA-256 hashes.')
