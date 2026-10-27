#!/usr/bin/env python3
"""Restore exact recorded evidence bytes from lossless gzip storage."""
from pathlib import Path, PurePosixPath
import gzip, hashlib, json, os
root=Path(__file__).resolve().parent
def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for row in json.loads((root/'COMPRESSED_DATA.json').read_text()):
    for key in ('path','stored_path'):
        p=PurePosixPath(row[key]);assert not p.is_absolute() and '..' not in p.parts
    src=root/row['stored_path'];dst=root/row['path']
    assert sha(src)==row['stored_sha256']
    if dst.exists():
        assert dst.stat().st_size==row['bytes'] and sha(dst)==row['sha256']
        print('Already verified:',row['path']);continue
    tmp=dst.with_name(dst.name+'.restoring');assert not tmp.exists()
    h=hashlib.sha256();count=0
    try:
        with gzip.open(src,'rb') as source,tmp.open('xb') as output:
            while block:=source.read(1024*1024):h.update(block);count+=len(block);output.write(block)
        assert count==row['bytes'] and h.hexdigest()==row['sha256']
        os.replace(tmp,dst)
    finally:
        if tmp.exists():tmp.unlink()
    print('Restored and verified:',row['path'])
