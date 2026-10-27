#!/usr/bin/env python3
"""Verify archived payload identity before rerunning audits, which rewrite evidence."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'FILE_MANIFEST.json').read_text());errors=[]
for item in manifest['files']:
    path=root/item['path']
    if not path.is_file():errors.append({'path':item['path'],'error':'missing'})
    elif path.stat().st_size!=item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
        errors.append({'path':item['path'],'error':'hash or length mismatch'})
print(json.dumps({'status':'PASS' if not errors else 'FAIL','files_checked':len(manifest['files']),'failures':errors},indent=2))
raise SystemExit(bool(errors))
