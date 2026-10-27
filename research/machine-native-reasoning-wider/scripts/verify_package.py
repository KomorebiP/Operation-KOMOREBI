#!/usr/bin/env python3
"""Strict size/SHA-256 and exact-file-set verification. Does not verify mathematical proofs."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys

MANIFEST='MANIFEST_SHA256.json'

def no_duplicate_keys(pairs):
    out={}
    for k,v in pairs:
        if k in out:raise ValueError(f'Duplicate JSON key: {k}')
        out[k]=v
    return out

def sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def check(root: Path) -> dict:
    if root.is_symlink():raise ValueError('Package root may not be a symbolic link')
    root=root.resolve()
    m=root/MANIFEST
    if not m.is_file() or m.is_symlink():raise ValueError('Missing regular manifest')
    data=json.loads(m.read_text(encoding='utf-8'),object_pairs_hook=no_duplicate_keys)
    if not isinstance(data,dict) or data.get('schema')!='mnr-files-v1':raise ValueError('Invalid manifest schema')
    rows=data.get('files')
    if not isinstance(rows,list):raise ValueError('Manifest files must be a list')
    expected={}
    for row in rows:
        if not isinstance(row,dict) or set(row)!={'path','bytes','sha256'}:raise ValueError('Invalid file row')
        name=row['path']
        if not isinstance(name,str):raise ValueError('Non-string file path')
        p=PurePosixPath(name)
        if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or p.as_posix()!=name or name==MANIFEST:
            raise ValueError(f'Unsafe or noncanonical path: {name!r}')
        if name in expected:raise ValueError(f'Duplicate path: {name}')
        if type(row['bytes']) is not int or row['bytes']<0:raise ValueError(f'Invalid size: {name}')
        if not isinstance(row['sha256'],str) or re.fullmatch(r'[0-9a-f]{64}',row['sha256']) is None:raise ValueError(f'Invalid SHA-256: {name}')
        expected[name]=row
    actual=set()
    for folder,dirs,files in os.walk(root,followlinks=False):
        base=Path(folder)
        for name in dirs:
            if (base/name).is_symlink():raise ValueError(f'Symlink directory: {base/name}')
        for name in files:
            p=base/name
            if p.is_symlink() or not p.is_file():raise ValueError(f'Not a regular file: {p}')
            rel=p.relative_to(root).as_posix()
            if rel!=MANIFEST:actual.add(rel)
    if actual!=set(expected):
        raise ValueError(f'File-set mismatch. Missing={sorted(set(expected)-actual)} Extra={sorted(actual-set(expected))}')
    for name,row in expected.items():
        p=root/name
        if p.stat().st_size!=row['bytes']:raise ValueError(f'Size mismatch: {name}')
        if sha(p)!=row['sha256']:raise ValueError(f'Hash mismatch: {name}')
    return {'status':'PASS','files':len(expected),'bytes':sum(r['bytes'] for r in rows),
            'scope':'Exact packaged file set, regular-file policy, byte lengths and SHA-256. Not a proof, execution, or authorship certificate.'}

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    a=ap.parse_args()
    try:report=check(a.root)
    except (OSError,ValueError,TypeError) as e:
        print(json.dumps({'status':'FAIL','error':str(e)},indent=2));return 1
    print(json.dumps(report,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
