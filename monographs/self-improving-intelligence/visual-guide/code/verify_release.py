#!/usr/bin/env python3
"""Check the frozen guide package before rebuilding files with timed receipts."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def main():
    inventory=json.loads((ROOT/'SHA256SUMS.json').read_text())
    errors=[]
    for name,expected in inventory['files'].items():
        p=ROOT/name
        if not p.resolve().is_relative_to(ROOT.resolve()):errors.append('Unsafe path: '+name)
        elif not p.is_file():errors.append('Missing: '+name)
        elif hashlib.sha256(p.read_bytes()).hexdigest()!=expected:errors.append('Changed: '+name)
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix.lower() in ('.ttf','.otf','.woff','.woff2','.ttc'):
            errors.append('Unexpected standalone font file: '+str(p.relative_to(ROOT)))
    if errors:
        print('\n'.join(errors));sys.exit(1)
    print(f"PASS: {len(inventory['files'])} frozen guide files. Integrity is not a proof of mathematical truth.")
if __name__=='__main__':main()
