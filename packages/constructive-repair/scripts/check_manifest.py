#!/usr/bin/env python3
"""Check listed source hashes and safe paths. Integrity, not author authentication."""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path,PurePosixPath

def check(root:Path, strict:bool=False)->dict:
    root=root.resolve();manifest=json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
    seen=set();total=0
    for rec in manifest['files']:
        name=rec['path'];rel=PurePosixPath(name)
        if (not name or rel.is_absolute() or '..' in rel.parts or '\\' in name
            or str(rel)!=name or name in seen):raise ValueError('Unsafe or duplicate manifest path: '+name)
        seen.add(name);p=root.joinpath(*rel.parts)
        if any(x.is_symlink() for x in [p,*p.parents] if x!=root and x.is_relative_to(root)):
            raise ValueError('Symlink in manifest path: '+name)
        if not p.is_file() or not p.resolve().is_relative_to(root):raise ValueError('Missing/escaping file: '+name)
        if p.stat().st_size!=rec['bytes']:raise ValueError('Byte count mismatch: '+name)
        h=hashlib.sha256()
        with p.open('rb') as stream:
            for b in iter(lambda:stream.read(1024*1024),b''):h.update(b)
        if h.hexdigest()!=rec['sha256']:raise ValueError('Hash mismatch: '+name)
        total+=rec['bytes']
    if strict:
        actual={str(p.relative_to(root)).replace('\\','/') for p in root.rglob('*') if p.is_file()}
        extra=actual-seen-{'MANIFEST.json','SHA256SUMS.txt'}
        if extra:raise ValueError('Unlisted files: '+repr(sorted(extra)[:8]))
    # This file binds the manifest itself as well as every listed artifact.
    hashes={}
    for line in (root/'SHA256SUMS.txt').read_text(encoding="utf-8").splitlines():
        digest,name=line.split('  ',1)
        if name in hashes:raise ValueError('Duplicate checksum entry')
        hashes[name]=digest
    if set(hashes)!=seen|{'MANIFEST.json'}:raise ValueError('Checksum coverage differs from manifest')
    if hashes['MANIFEST.json']!=hashlib.sha256((root/'MANIFEST.json').read_bytes()).hexdigest():
        raise ValueError('Manifest checksum mismatch')
    if any(hashes[r['path']]!=r['sha256'] for r in manifest['files']):raise ValueError('Checksum list mismatch')
    return {'status':'PASS','files':len(seen),'bytes':total,'strict':strict,
            'scope':'File integrity only; not a signature or mathematical proof'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--strict',action='store_true');a=p.parse_args()
    try:print(json.dumps(check(a.root,a.strict),indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as e:print(json.dumps({'status':'FAIL','error':str(e)}));return 2
if __name__=='__main__':raise SystemExit(main())
