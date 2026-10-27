#!/usr/bin/env python3
"""Verify the frozen collection bytes. Hash equality is not proof of truth."""
import hashlib,json,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    inventory=json.loads((ROOT/'SHA256SUMS.json').read_text())
    failures=[]
    for name,expected in inventory['files'].items():
        p=ROOT/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected:failures.append(name)
    for p in (ROOT/'source_archives').glob('*.zip'):
        with zipfile.ZipFile(p) as z:
            bad=z.testzip()
            if bad:failures.append(str(p.relative_to(ROOT))+':'+bad)
    result={'status':'PASS' if not failures else 'FAIL','files_checked':len(inventory['files']),'failures':failures,'scope':'Snapshot integrity and nested source ZIP CRCs, not mathematical validation or origin authentication.'}
    print(json.dumps(result,indent=2))
    return bool(failures)
if __name__=='__main__':sys.exit(main())
