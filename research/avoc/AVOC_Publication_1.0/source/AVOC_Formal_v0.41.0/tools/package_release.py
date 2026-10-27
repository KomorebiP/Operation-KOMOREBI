#!/usr/bin/env python3
"""Package the checked source/evidence tree; exclude generated binary caches.

Run the verification collector first. This operation creates integrity evidence,
not a proof-verification result. Packaging report is placed outside the payload
so it cannot create a self-referential hash manifest.
"""
from pathlib import Path
import hashlib, json, zipfile
ROOT = Path(__file__).resolve().parents[1]

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def selected(p: Path) -> bool:
    rel = p.relative_to(ROOT)
    return (p.is_file() and not p.is_symlink()
            and not ({'.lake','__pycache__','.git'} & set(rel.parts))
            and p.suffix not in {'.pyc','.olean','.ilean','.trace'}
            and rel.as_posix() != 'SHA256SUMS.txt')

files = sorted(p for p in ROOT.rglob('*') if selected(p))
lines = [f'{digest(p)}  {p.relative_to(ROOT).as_posix()}' for p in files]
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n')
files.append(ROOT/'SHA256SUMS.txt')
output = ROOT.parent / (ROOT.name + '.zip')
with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files:
        z.write(p,arcname=ROOT.name+'/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(output) as z:
    bad=z.testzip()
    if bad is not None: raise RuntimeError('ZIP CRC failure: '+bad)
    for p in files:
        if z.read(ROOT.name+'/'+p.relative_to(ROOT).as_posix()) != p.read_bytes():
            raise RuntimeError('ZIP payload mismatch: '+str(p))
report={'archive':str(output),'sha256':digest(output),'size_bytes':output.stat().st_size,
        'payload_files':len(files),'manifest_verified_files':len(lines),
        'zip_crc_pass':True,'exact_payload_match':True}
ROOT.with_name(ROOT.name+'_Packaging.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
