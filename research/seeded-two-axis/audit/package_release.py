#!/usr/bin/env python3
"""Inventory and package the release; does not validate mathematical proofs."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT.parent/(ROOT.name+'_Full_Package.zip')

def sha(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def included(p:Path)->bool:
    rel=p.relative_to(ROOT)
    if not p.is_file():return False
    if any(x in {'build','__pycache__','.git'} for x in rel.parts):return False
    if p.suffix.lower() in {'.pyc','.pfb','.pfa','.ttf','.otf','.woff','.woff2'}:return False
    return rel.as_posix()!='SHA256SUMS.json'

def main():
    files=sorted(p for p in ROOT.rglob('*') if included(p))
    sums={p.relative_to(ROOT).as_posix():sha(p) for p in files}
    inv=ROOT/'SHA256SUMS.json';inv.write_text(json.dumps(sums,indent=2)+'\n')
    with zipfile.ZipFile(OUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files+[inv]:z.write(p,ROOT.name+'/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(OUT) as z:
        assert z.testzip() is None
        for rel,dig in sums.items():
            assert hashlib.sha256(z.read(ROOT.name+'/'+rel)).hexdigest()==dig,rel
        assert len(z.infolist())==len(files)+1
    report={'status':'PASS','package':OUT.name,'bytes':OUT.stat().st_size,'file_count':len(files)+1,
            'zip_integrity':True,'all_entries_match_checksums':True,'sha256':sha(OUT),
            'excluded':['build intermediates','Python bytecode','standalone font files'],
            'scope':'Byte integrity and file inventory, not mathematical certification.'}
    dest=ROOT.parent/(ROOT.name+'_Package_Check.json')
    dest.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
