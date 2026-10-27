#!/usr/bin/env python3
"""Verify a frozen archive snapshot before rerunning programs that change receipts."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    inventory=ROOT/'SHA256SUMS.json'
    if not inventory.is_file():raise SystemExit('Missing release inventory.')
    record=json.loads(inventory.read_text());files=record['files'];errors=[]
    for relative,expected in files.items():
        path=ROOT/relative
        if not path.resolve().is_relative_to(ROOT.resolve()):errors.append(f'Invalid path: {relative}')
        elif not path.is_file():errors.append(f'Missing: {relative}')
        elif sha(path)!=expected:errors.append(f'Changed: {relative}')
    manifest=ROOT/'validation'/'execution_manifest.json'
    if manifest.is_file():
        m=json.loads(manifest.read_text())
        if m['status']!='PASS' or m['inputs_before']!=m['inputs_after']:errors.append('Incomplete or changed-input execution record.')
        for rel,digest in m['inputs_after'].items():
            if not (ROOT/rel).is_file() or sha(ROOT/rel)!=digest:errors.append(f'Execution input changed: {rel}')
        for rel,digest in m['outputs'].items():
            if not (ROOT/rel).is_file() or sha(ROOT/rel)!=digest:errors.append(f'Execution output changed: {rel}')
    else:errors.append('Missing execution record.')
    if errors:raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(files)} archived files and the pinned execution inputs/outputs.')
    print('This verifies recorded integrity, not mathematical truth or independent execution.')
if __name__=='__main__':main()
