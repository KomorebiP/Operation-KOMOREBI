#!/usr/bin/env python3
"""Strict SHA-256 and file-set verification for the delivered Paper XII tree."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def verify(root:Path):
    root=root.resolve();mp=root/'MANIFEST_SHA256.json'
    m=json.loads(mp.read_text());rows=m['files'];expected={r['path'] for r in rows}
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and p!=mp}
    errors=[]
    for r in rows:
        p=root/r['path']
        if root not in p.resolve().parents:errors.append('Unsafe path '+r['path']);continue
        if not p.is_file():errors.append('Missing '+r['path']);continue
        h=hashlib.sha256(p.read_bytes()).hexdigest()
        if h!=r['sha256'] or p.stat().st_size!=r['bytes']:errors.append('Mismatch '+r['path'])
    if actual-expected:errors.append('Unexpected files: '+repr(sorted(actual-expected)))
    return {'status':'PASS' if not errors else 'FAIL','manifest_entries':len(rows),'root':str(root),'errors':errors}
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=ROOT);ap.add_argument('--output',type=Path);a=ap.parse_args()
    if a.output and (a.root.resolve()==a.output.resolve().parent or a.root.resolve() in a.output.resolve().parents):raise ValueError('Write verification output outside the checked tree')
    r=verify(a.root);s=json.dumps(r,indent=2)+'\n';print(s)
    if a.output:a.output.write_text(s)
    raise SystemExit(r['status']!='PASS')
