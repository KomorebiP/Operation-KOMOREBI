#!/usr/bin/env python3
"""Verify every manifested file in this extracted package. No external dependencies."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
p=root/'MANIFEST_SHA256.json'
if not p.exists():raise SystemExit('Manifest is missing; package is not finalized.')
m=json.loads(p.read_text());fail=[]
if m['count']!=len(m['files']):fail.append('manifest count')
for r in m['files']:
 f=root/r['path']
 if not f.is_file() or f.stat().st_size!=r['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest()!=r['sha256']:
  fail.append(r['path'])
if fail:
 print('FAIL:',*fail,sep='\n');sys.exit(1)
print(f"BUNDLE_PASS {len(m['files'])} manifested payload files")
