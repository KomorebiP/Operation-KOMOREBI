#!/usr/bin/env python3
"""Manifest, package and independently verify every payload in the completed handoff."""
from pathlib import Path
import hashlib,json,sys,zipfile
root=Path(__file__).resolve().parents[1]
receipt=json.loads((root/'VERIFICATION.json').read_text())
if receipt['status']!='PASS':raise SystemExit('Refusing non-PASS release')
# Remove only transient bytecode outside the immutable predecessor.
for p in (root/'scripts').rglob('*.pyc'):p.unlink()
for p in sorted((root/'scripts').rglob('__pycache__'),reverse=True):
 if p.is_dir() and not any(p.iterdir()):p.rmdir()
files=[]
for p in sorted(root.rglob('*')):
 if p.is_file() and p!=root/'MANIFEST_SHA256.json':
  files.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
man={'schema':'komorebi.completion.manifest/0.4.0','algorithm':'sha256','excluded':['MANIFEST_SHA256.json'],'count':len(files),'files':files}
(root/'MANIFEST_SHA256.json').write_text(json.dumps(man,indent=2)+'\n')
out=Path(sys.argv[1]) if len(sys.argv)>1 else root.parent/(root.name+'.zip')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(root.rglob('*')):
  if p.is_file():z.write(p,str(Path(root.name)/p.relative_to(root)))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert len(z.namelist())==len(files)+1
 assert len(set(z.namelist()))==len(z.namelist())
 assert json.loads(z.read(root.name+'/MANIFEST_SHA256.json'))==man
 for x in files:
  raw=z.read(root.name+'/'+x['path']);assert len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest()==x['sha256'],x['path']
result={'status':'PASS','zip':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'manifested_payloads':len(files),'zip_members':len(files)+1,'crc_check':'PASS','all_payload_hashes':'PASS'}
print(json.dumps(result,indent=2))
