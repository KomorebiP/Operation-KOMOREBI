#!/usr/bin/env python3
"""Package current sources/evidence; excludes runtime, build products and caches."""
from pathlib import Path
import hashlib,json,zipfile
R=Path(__file__).resolve().parents[1]
summary=json.loads((R/'results/v0.22.0/verification_summary.json').read_text())
assert summary['passed']
(R/'AUDIT.json').write_text(json.dumps({'release':'0.22.0',**summary},indent=2)+'\n')
excluded={'.lake','.git','__pycache__'}
files=sorted(p for p in R.rglob('*') if p.is_file() and not excluded.intersection(p.relative_to(R).parts)
    and p.suffix not in {'.pyc','.olean','.ilean','.ttf','.otf','.woff','.woff2'} and p.name!='SHA256SUMS.txt')
hashes={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(R/'SHA256SUMS.txt').write_text(''.join(f'{h}  {n}\n' for n,h in hashes.items()))
out=R.parent/(R.name+'.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in files+[R/'SHA256SUMS.txt']:z.write(p,R.name+'/'+str(p.relative_to(R)))
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
    for n,h in hashes.items():assert hashlib.sha256(z.read(R.name+'/'+n)).hexdigest()==h
record={'archive':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
    'bytes':out.stat().st_size,'matched_payloads':len(hashes),'zip_entries':len(hashes)+1,'zip_crc':'PASS'}
(R.parent/'AVOC_v022_delivery.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
