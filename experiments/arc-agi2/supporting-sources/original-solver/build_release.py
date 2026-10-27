"""Deterministic complete package builder. Author: Komorebi P."""
from __future__ import annotations
import argparse,hashlib,json,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def file_hash(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def inventory(root):
    rows={}
    for p in sorted(root.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc':continue
        if any(part.startswith('.') for part in p.relative_to(root).parts) or p.name.endswith('.partial'):continue
        # Final complete census supersedes transient per-task checkpoints.
        if p.relative_to(root).parts[0]=='results' and any(part.endswith('.tasks') for part in p.relative_to(root).parts):continue
        if p.name in {'release_manifest.json'}:continue
        if p.relative_to(root).as_posix()=='results/final_legacy_census.json':continue
        rows[p.relative_to(root).as_posix()]={'sha256':file_hash(p),'bytes':p.stat().st_size}
    return rows

def build(root,output):
    root=Path(root).resolve();output=Path(output).resolve()
    rows=inventory(root)
    manifest={'schema':'komorebi.block17.release_manifest.v1','author':'Komorebi P.','files':rows,
              'checkpoint_policy':'Canonical working checkpoints omitted; final census, pre-score partial scans and restart rejection receipts retained.'}
    payload=json.dumps(manifest,sort_keys=True,indent=2).encode()+b'\n'
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in sorted([*rows,'release_manifest.json']):
            info=zipfile.ZipInfo('block17/'+name,date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16;info.create_system=3
            data=payload if name=='release_manifest.json' else (root/name).read_bytes()
            z.writestr(info,data,compresslevel=9)
    return {'file':output.name,'bytes':output.stat().st_size,'sha256':file_hash(output),'files':len(rows)+1}

def verify_archive(path):
    with zipfile.ZipFile(path) as z:
        manifest=json.loads(z.read('block17/release_manifest.json'))
        expected={'block17/'+n for n in manifest['files']}|{'block17/release_manifest.json'}
        if set(z.namelist())!=expected:raise AssertionError('archive inventory mismatch')
        for name,row in manifest['files'].items():
            data=z.read('block17/'+name)
            if hashlib.sha256(data).hexdigest()!=row['sha256'] or len(data)!=row['bytes']:raise AssertionError('archive content mismatch')
    return True

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=build(a.root,a.output);r['manifest_verified']=verify_archive(a.output);print(json.dumps(r,indent=2))
