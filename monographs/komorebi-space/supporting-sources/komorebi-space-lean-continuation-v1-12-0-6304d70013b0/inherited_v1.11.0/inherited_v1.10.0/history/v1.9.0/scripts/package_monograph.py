#!/usr/bin/env python3
"""Assemble a versioned publication; preserve accepted inherited evidence bytes."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent
PREVIOUS = WORK / 'output/Komorebi_Space_Formal_Continuation_v1.8.0'
DEST = WORK / 'output/Komorebi_Space_Monograph_v1.9.0'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(p): return {str(q.relative_to(p)):sha(q) for q in sorted(p.rglob('*')) if q.is_file()}

def main():
    if DEST.exists(): raise SystemExit('Refusing to overwrite an existing release directory')
    DEST.mkdir()
    for name in ['source','scripts','reviews','audit']:
        shutil.copytree(ROOT/name,DEST/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for name in ['formal','continuation','inherited_v1.7.0']:
        shutil.copytree(PREVIOUS/name,DEST/name)
        if tree(PREVIOUS/name)!=tree(DEST/name): raise SystemExit('Inherited identity mismatch: '+name)
    shutil.copytree(PREVIOUS/'inherited_v1.7.0/examples',DEST/'examples')
    (DEST/'publication').mkdir()
    pdf=ROOT/'publication/Komorebi_Space_Monograph.pdf'
    shutil.copy2(pdf,DEST/'publication/Komorebi_Space_Monograph_v1.9.0.pdf')
    for name in ['README.md','PROGRESS_LEDGER.md','PROGRESS_LEDGER.json','PUBLICATION_VERIFICATION.json']:
        shutil.copy2(ROOT/name,DEST/name)
    history=DEST/'history/v1.8.0'
    history.mkdir(parents=True)
    for name in ['README.md','PROGRESS_LEDGER.md','PROGRESS_LEDGER.json','VERIFICATION_SUMMARY.json','SHA256SUMS.txt']:
        shutil.copy2(PREVIOUS/name,history/name)
    payload=tree(DEST)
    (DEST/'SHA256SUMS.txt').write_text(''.join(f'{digest}  {name}\n' for name,digest in payload.items()))
    archive=DEST.parent/(DEST.name+'.zip')
    if archive.exists(): raise SystemExit('Refusing to overwrite an existing archive')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file(): z.write(p,str(Path(DEST.name)/p.relative_to(DEST)))
    with zipfile.ZipFile(archive) as z:
        bad=z.testzip()
        if bad: raise SystemExit('ZIP CRC failure: '+bad)
        for name,digest in payload.items():
            data=z.read(str(Path(DEST.name)/name))
            if hashlib.sha256(data).hexdigest()!=digest: raise SystemExit('ZIP payload mismatch: '+name)
    standalone=WORK/'output/Komorebi_Space_Monograph_v1.9.0.pdf'
    shutil.copy2(pdf,standalone)
    result={'archive':str(archive),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,
            'payload_files':len(payload),'crc':'PASS','payload_sha256':'PASS',
            'inherited_trees_byte_identical':True,
            'pdf':str(standalone),'pdf_sha256':sha(standalone)}
    (WORK/'output/Komorebi_Space_Delivery_Verification_v1.9.0.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
