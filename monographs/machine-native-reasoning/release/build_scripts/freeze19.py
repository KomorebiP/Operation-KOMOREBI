#!/usr/bin/env python3
"""Freeze every current proof-gate input and extract an independent clean source tree.

No gate is launched by this script. Refuses existing snapshot/receipt or a
nonempty fresh directory. The snapshot is hash-bound to the verifier input set.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for b in iter(lambda:stream.read(4<<20), b''):h.update(b)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fresh',type=Path,required=True)
    ap.add_argument('--archive',type=Path,default=ROOT/'evidence/CORE32_FROZEN_SOURCE.zip')
    ap.add_argument('--receipt',type=Path,default=ROOT/'evidence/SOURCE_SNAPSHOT_BLOCK19.json')
    args=ap.parse_args()
    archive=args.archive.resolve(); receipt=args.receipt.resolve();fresh=args.fresh.resolve()
    if archive.exists() or receipt.exists():raise FileExistsError('Snapshot or receipt already exists')
    if fresh.exists() and any(fresh.iterdir()):raise FileExistsError('Fresh directory is not empty')
    spec=importlib.util.spec_from_file_location('current_verifier',ROOT/'scripts/verify.py')
    verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)
    pins=verifier.source_pins()
    if not pins:raise ValueError('No proof inputs')
    archive.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for rel in sorted(pins):
            if rel.endswith(('.olean','.ilean','.c','.o')):raise ValueError('Compiled project input: '+rel)
            data=(ROOT/rel).read_bytes()
            if hashlib.sha256(data).hexdigest()!=pins[rel]:raise ValueError('Input changed while freezing: '+rel)
            info=zipfile.ZipInfo(rel,date_time=(2026,10,25,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,data)
    fresh.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Snapshot CRC failure')
        if len(z.namelist())!=len(pins) or set(z.namelist())!=set(pins):raise ValueError('Snapshot membership mismatch')
        for name in z.namelist():
            path=Path(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name:raise ValueError('Unsafe source member')
        z.extractall(fresh)
    if not all(sha(fresh/rel)==expected for rel,expected in pins.items()):raise ValueError('Fresh source hash mismatch')
    if verifier.source_pins()!=pins:raise ValueError('Live inputs changed during snapshot creation')
    record={'schema':'komorebi.block19.source-snapshot.v1','status':'PASS',
        'archive':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,
        'source_inputs':pins,'source_count':len(pins),'fresh_tree':str(fresh),
        'contains_project_objects':False,'scope':'All proof-gate input bytes; no claim of compilation or source-result admission.'}
    receipt.parent.mkdir(parents=True,exist_ok=True)
    receipt.write_text(json.dumps(record,indent=2)+'\n')
    print('Frozen',len(pins),'inputs;',sha(archive),'; clean tree',fresh)

if __name__=='__main__':main()
