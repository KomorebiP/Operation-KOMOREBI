#!/usr/bin/env python3
"""Portable SHA-256 verification of a Paper III private scoped handoff."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parent
manifest=root/'MANIFEST_SHA256_v1.0.0_rc1.json'
obj=json.loads(manifest.read_text())
expected={r['path']:r for r in obj['files']}
seen={str(x.relative_to(root)) for x in root.rglob('*') if x.is_file() and x!=manifest}
errors=[]
if expected.keys()!=seen:
 errors += ['Missing: '+str(sorted(expected.keys()-seen)[:8]), 'Extra: '+str(sorted(seen-expected.keys())[:8])]
for path,row in expected.items():
 f=root/path
 if not f.is_file():continue
 if f.is_symlink(): errors.append('Symlink prohibited: '+path);continue
 data=f.read_bytes()
 if len(data)!=row['size_bytes'] or hashlib.sha256(data).hexdigest()!=row['sha256']:
  errors.append('Hash/size mismatch: '+path)
font_ext={'.ttf','.otf','.woff','.woff2','.pfb','.pfm'}
fonts=[p for p in seen if Path(p).suffix.lower() in font_ext]
if fonts:errors.append('Source font file is present: '+str(fonts[:3]))
status='PASS' if not errors else 'FAIL'
print(json.dumps({'status':status,'manifest_entries':len(expected),'file_count':len(seen),'errors':errors},indent=2))
sys.exit(0 if not errors else 1)
