#!/usr/bin/env python3
"""Package a completed audited checkpoint and verify every archived payload."""
from pathlib import Path
import hashlib,json,zipfile
r=Path(__file__).resolve().parents[1]
assert json.loads((r/'VERIFICATION.json').read_text())['status']=='PASS'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Preserve every predecessor manifest; omit only this release's own manifest from self-hashing.
files=sorted(p for p in r.rglob('*') if p.is_file() and p!=r/'MANIFEST_SHA256.json' and '__pycache__' not in p.parts)
rows=[{'path':str(p.relative_to(r)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
manifest={'schema':'komorebi-sha256-manifest/0.5.0','count':len(rows),'files':rows}
(r/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
out=r.parent/(r.name+'.zip')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in files+[r/'MANIFEST_SHA256.json']:z.write(p,r.name+'/'+str(p.relative_to(r)))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(rows)+1
 stored=json.loads(z.read(r.name+'/MANIFEST_SHA256.json'))
 assert stored==manifest
 for row in rows:
  data=z.read(r.name+'/'+row['path']);assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
receipt={'status':'PASS','archive':str(out),'archive_bytes':out.stat().st_size,'archive_sha256':sha(out),'archive_crc_check':'PASS','manifested_payloads_verified':len(rows),'archive_entries':len(rows)+1,'manifest_sha256':sha(r/'MANIFEST_SHA256.json')}
(r.parent/'Paper_I_Block05_Archive_Verification_2026-10-10.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
