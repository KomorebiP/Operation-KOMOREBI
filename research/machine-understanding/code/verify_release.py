#!/usr/bin/env python3
"""Verify frozen release hashes and declared receipt counts, not semantic correctness."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[];count=0
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        if not line.strip():continue
        expected,name=line.split('  ',1);path=(ROOT/name).resolve();count+=1
        if not path.is_relative_to(ROOT):errors.append('Unsafe path: '+name)
        elif not path.is_file():errors.append('Missing: '+name)
        elif hashlib.sha256(path.read_bytes()).hexdigest()!=expected:errors.append('Changed: '+name)
    p=ROOT/'validation/final/computation_manifest.json'
    if not p.is_file():errors.append('Missing finite validation record.')
    else:
        m=json.loads(p.read_text())
        if m.get('run',{}).get('exit_status')!=0 or m.get('group_count')!=38 or m.get('assertions')!=252669:
            errors.append('Finite record differs from declared edition.')
    print(json.dumps({'status':'passed' if not errors else 'failed','files_checked':count,'errors':errors},indent=2))
    if errors:raise SystemExit(1)
if __name__=='__main__':main()
