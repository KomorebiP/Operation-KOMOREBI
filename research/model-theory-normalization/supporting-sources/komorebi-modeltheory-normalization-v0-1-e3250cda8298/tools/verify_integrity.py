#!/usr/bin/env python3
"""Check release payload hashes before rerunning any mutating audit commands."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    m=json.loads((ROOT/'FILE_MANIFEST.json').read_text());fail=[]
    for x in m['files']:
        p=(ROOT/x['path']).resolve()
        if not p.is_relative_to(ROOT.resolve()):fail.append([x['path'],'unsafe path']);continue
        if not p.is_file():fail.append([x['path'],'missing']);continue
        if p.stat().st_size!=x['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:
            fail.append([x['path'],'size/hash mismatch'])
    print(json.dumps({'status':'PASS' if not fail else 'FAIL','files_checked':len(m['files']),'failures':fail},indent=2))
    if fail:raise SystemExit(1)
if __name__=='__main__':main()
