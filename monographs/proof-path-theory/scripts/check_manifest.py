"""Verify the exact files recorded in the unpacked release's SHA-256 manifest."""
from __future__ import annotations
import hashlib
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]

def main():
    entries=(ROOT/'MANIFEST.sha256').read_text().splitlines()
    for line in entries:
        expected, relative=line.split('  ',1)
        pure=PurePosixPath(relative)
        if pure.is_absolute() or '..' in pure.parts:
            raise ValueError('unsafe manifest path')
        path=ROOT/relative
        if not path.is_file():raise FileNotFoundError(path)
        h=hashlib.sha256()
        with path.open('rb') as handle:
            for chunk in iter(lambda:handle.read(1024*1024),b''):h.update(chunk)
        if h.hexdigest()!=expected:raise RuntimeError('hash mismatch: '+relative)
    print(f'PASS: {len(entries)} manifest entries match.')
if __name__=='__main__':main()
