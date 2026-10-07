#!/usr/bin/env python3
"""Verify the shipped edition's file manifest without changing any source."""
from pathlib import Path
import hashlib, json, sys

root=Path(__file__).resolve().parent.parent
manifest=json.loads((root/'MANIFEST_SHA256.json').read_text())
failures=[]
for item in manifest['files']:
    p=root/item['path']
    if not p.is_file(): failures.append({'path':item['path'],'problem':'missing'})
    elif hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:
        failures.append({'path':item['path'],'problem':'checksum differs'})
print(json.dumps({'status':'FAIL' if failures else 'PASS','files_checked':len(manifest['files']),'failures':failures},indent=2))
sys.exit(bool(failures))
