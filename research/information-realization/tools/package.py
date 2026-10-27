#!/usr/bin/env python3
"""Write a source-only handoff with checksums; never ship cached object files."""
from pathlib import Path
import hashlib, json, zipfile
ROOT = Path(__file__).resolve().parents[1]
def members():
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file(): continue
        rel = p.relative_to(ROOT)
        if any(s in {'.lake','__pycache__','.git'} for s in rel.parts): continue
        if p.name in {'MANIFEST_SHA256.json','DELIVERY_CHECKS.json'}: continue
        if p.suffix in {'.olean','.ilean','.c','.o','.so'}: continue
        yield p

def package(destination: Path):
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in members()}
    (ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    check = dict(source_manifest_entries=len(hashes),
                 unique_named_theorems=len(json.loads((ROOT/'DECLARATIONS.json').read_text())),
                 excludes_project_and_external_build_caches=True,
                 runtime_included=False,prior_v03_retained=True,
                 prior_v03_sha256=hashes['prior/komorebi_information_realization_v0_3.zip'])
    (ROOT/'DELIVERY_CHECKS.json').write_text(json.dumps(check,indent=2)+'\n')
    allfiles=list(members())+[ROOT/'MANIFEST_SHA256.json',ROOT/'DELIVERY_CHECKS.json']
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in allfiles:
            z.write(p,str(Path(ROOT.name)/p.relative_to(ROOT)))
    with zipfile.ZipFile(destination) as z:
        bad=z.testzip()
        if bad: raise RuntimeError(f'ZIP CRC failed at {bad}')
        for rel,sha in hashes.items():
            if hashlib.sha256(z.read(f'{ROOT.name}/{rel}')).hexdigest()!=sha:
                raise RuntimeError(f'Manifest verification failed for {rel}')
    return dict(path=str(destination),size=destination.stat().st_size,
                sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),members=len(allfiles))
if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('output',type=Path)
    args=ap.parse_args()
    print(json.dumps(package(args.output),indent=2))
