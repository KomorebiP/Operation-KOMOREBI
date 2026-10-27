#!/usr/bin/env python3
"""Validate complete delivery integrity and the core's recorded checks."""
from pathlib import Path, PurePosixPath
import json, hashlib, subprocess, sys
root=Path(__file__).resolve().parent
try:
 rows=json.loads((root/'BUNDLE_MANIFEST.json').read_text())['files']
 names=set()
 for item in rows:
  name=item['path'];p=PurePosixPath(name)
  if p.is_absolute() or '..' in p.parts or '\\' in name or name in names:raise ValueError('Unsafe or duplicate path')
  names.add(name);f=root/name
  if f.is_symlink() or not f.is_file() or f.stat().st_size!=item['bytes']:raise ValueError('Missing or altered member '+name)
  with f.open('rb') as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
  if digest!=item['sha256']:raise ValueError('Hash mismatch '+name)
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
 if actual!=names|{'BUNDLE_MANIFEST.json'}:raise ValueError('Unexpected file set')
 p=subprocess.run([sys.executable,'-B',str(root/'Paper_IV_Verification_Closeout_v1.1.0/scripts/verify_release.py')])
 if p.returncode!=0:raise ValueError('Core verification failed')
 print('COMPLETE_DELIVERY_PASS',len(rows)+1,'files')
except Exception as exc:
 print('COMPLETE_DELIVERY_FAILED',str(exc),file=sys.stderr);sys.exit(1)
