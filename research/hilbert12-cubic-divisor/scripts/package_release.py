#!/usr/bin/env python3
"""Build a source manifest and ZIP of this edition, excluding caches and runtimes."""
from collections import Counter
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import os
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_PARTS = {'.lake', '.git', '__pycache__', '.pytest_cache'}
EXCLUDED_SUFFIXES = {'.pyc', '.aux', '.toc', '.out', '.fls', '.fdb_latexmk', '.synctex.gz'}

def files():
    selected=[]
    for path in ROOT.rglob('*'):
        rel=path.relative_to(ROOT)
        if not path.is_file() or path.is_symlink():continue
        if any(part in EXCLUDED_PARTS for part in rel.parts):continue
        if path.suffix in EXCLUDED_SUFFIXES:continue
        if rel.as_posix()=='SOURCE_MANIFEST.json':continue
        selected.append(path)
    return sorted(selected)

def main():
    selected=files()
    records=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in selected]
    counts=dict(sorted(Counter(p.suffix for p in selected).items()))
    manifest={'edition':'2026-10-07','file_count_excluding_manifest':len(records),
              'counts_by_extension':counts,'files':records,
              'scope':'Publication, editable sources, figures, engine and evidence; dependency/runtime caches excluded.'}
    target=ROOT/'SOURCE_MANIFEST.json'
    target.write_text(json.dumps(manifest,indent=2)+'\n')
    archive=ROOT.parent/(ROOT.name+'.zip')
    fd, temporary = tempfile.mkstemp(prefix=ROOT.name+'.',suffix='.zip.tmp',dir=ROOT.parent)
    os.close(fd)
    staging=Path(temporary)
    with ZipFile(staging,'w',compression=ZIP_DEFLATED,compresslevel=6) as z:
        for path in selected+[target]:
            z.write(path,ROOT.name+'/'+path.relative_to(ROOT).as_posix())
    with ZipFile(staging) as z:
        bad=z.testzip()
        if bad:raise RuntimeError('ZIP integrity failed: '+bad)
        names=z.namelist()
        if len(names)!=len(set(names)):raise RuntimeError('Duplicate ZIP entries')
        for record in records:
            content=z.read(ROOT.name+'/'+record['path'])
            if hashlib.sha256(content).hexdigest()!=record['sha256']:
                raise RuntimeError('ZIP source hash mismatch: '+record['path'])
    staging.replace(archive)
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,
          'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
          'members':len(names),'crc_and_manifest_hashes':'PASS'},indent=2))

if __name__=='__main__':main()
