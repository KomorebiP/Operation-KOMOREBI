#!/usr/bin/env python3
"""Manifest, package, and verify every payload after a completed handoff."""
from pathlib import Path
import hashlib,json,zipfile,shutil
r=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
v=json.loads((r/'VERIFICATION.json').read_text());assert v['status']=='PASS'
post=json.loads((r/'evidence/HANDOFF_POSTFLIGHT.json').read_text())
assert post['status']=='PASS' and post['active_audit_or_compiler_processes']==[]
for p in list(r.rglob('__pycache__')):
 if 'predecessor' not in p.relative_to(r).parts:shutil.rmtree(p)
files=sorted(p for p in r.rglob('*') if p.is_file() and p!=r/'MANIFEST_SHA256.json')
assert not any(p.suffix.lower() in {'.ttf','.otf','.woff','.woff2'} for p in files)
rows=[{'path':str(p.relative_to(r)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files]
manifest={'schema':'sha256-payload-manifest/1','count':len(rows),'files':rows}
(r/'MANIFEST_SHA256.json').write_text(json.dumps(manifest,indent=2)+'\n')
zp=r.parent/(r.name+'.zip')
with zipfile.ZipFile(zp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in [*files,r/'MANIFEST_SHA256.json']:z.write(p,str(Path(r.name)/p.relative_to(r)))
with zipfile.ZipFile(zp) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(rows)+1
 for row in rows:
  data=z.read(r.name+'/'+row['path'])
  assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],row['path']
 assert z.read(r.name+'/MANIFEST_SHA256.json')==(r/'MANIFEST_SHA256.json').read_bytes()
receipt={'status':'PASS','zip':zp.name,'zip_bytes':zp.stat().st_size,'zip_sha256':sha(zp),
 'manifested_payloads_verified':len(rows),'archive_files_including_manifest':len(rows)+1,
 'zip_integrity':'PASS','manifest_sha256':sha(r/'MANIFEST_SHA256.json')}
(r.parent/'Paper_I_Block06_Archive_Verification_2026-10-11.json').write_text(json.dumps(receipt,indent=2)+'\n')
exports={
'docs/COMPLETION_REPORT.md':'Paper_I_Block06_Completion_Report_2026-10-11.md',
'docs/PROOF_GUIDE.md':'Paper_I_Block06_Proof_Guide_2026-10-11.md',
'VERIFICATION.json':'Paper_I_Block06_Verification_2026-10-11.json',
'PROGRESS_LEDGER.md':'Paper_I_Block06_Progress_Ledger_v0.6.0.md',
'coverage/COVERAGE_108.md':'Paper_I_Expanded_108_Record_Lean_Coverage_v0.6.0.md'}
for src,dest in exports.items():shutil.copy2(r/src,r.parent/dest)
print(json.dumps(receipt,indent=2))
