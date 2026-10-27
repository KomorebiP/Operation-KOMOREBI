#!/usr/bin/env python3
"""Check frozen release bytes and declared PDF/source identities. No proof checking."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def sha(path: Path) -> str:
    digest=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',default='MANIFEST_SHA256.json')
    args=ap.parse_args();errors=[]
    try:
        data=json.loads((ROOT/args.manifest).read_text())
        rows=data['files'];seen=set()
        for row in rows:
            rel=row['path'];p=(ROOT/rel).resolve()
            if not p.is_relative_to(ROOT) or rel in seen:errors.append('Invalid or duplicate path: '+rel);continue
            seen.add(rel)
            if not p.is_file():errors.append('Missing: '+rel);continue
            if p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:errors.append('Changed: '+rel)
        release=json.loads((ROOT/'RELEASE.json').read_text())
        for row in release['documents']:
            for key in ('file','mirror'):
                p=ROOT/row[key]
                if not p.is_file() or sha(p)!=row['sha256']:errors.append('PDF identity: '+row[key])
        for rel,expected in release['source_revision'].items():
            if not (ROOT/rel).is_file() or sha(ROOT/rel)!=expected:errors.append('Source revision: '+rel)
    except (OSError,KeyError,ValueError) as e:
        errors.append(str(e));rows=[]
    print(json.dumps({'status':'PASS' if not errors else 'FAIL','files_checked':len(rows),'errors':errors,'scope':'Frozen byte integrity and declared identity consistency. Not a proof audit, authenticity signature, or fresh Lean compilation.'},indent=2))
    raise SystemExit(bool(errors))
if __name__=='__main__':main()
