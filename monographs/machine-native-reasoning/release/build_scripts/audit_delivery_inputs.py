from pathlib import Path
import json,hashlib,sys,importlib.util,time,shutil
sys.dont_write_bytecode=True
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25');B=Path('/mnt/data/core25/Machine_Native_Reasoning_Lean_Core24')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cache=B/'tools/__pycache__/verify_package.cpython-313.pyc'
if cache.exists():
 (R/'evidence/HOST_METADATA_RECHECK_FAILURE.json').write_text(json.dumps({'failure':'Strict predecessor verifier rejected the Python bytecode cache created by an import of that verifier.','extra_path':str(cache.relative_to(B)),'extra_sha256':sha(cache),'resolution':'Remove only this newly generated local cache, disable bytecode creation, and rerun exact-set verification. Original archive and all payload bytes are unchanged.'},indent=2)+'\n')
 cache.unlink();cache.parent.rmdir()
s=importlib.util.spec_from_file_location('vp',B/'tools/verify_package.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
start=time.monotonic();d=v.verify(B)
a=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core24_v0.17.1.zip');delivery=json.loads(Path('/mnt/data/Machine_Native_Reasoning_Lean_Core24_Verification.json').read_text());snapshot=B/'evidence/CORE24_FROZEN_SOURCE.zip'
r={'schema':'komorebi.core25.predecessor-authentication.v1','status':'PASS','archive_bytes':a.stat().st_size,'archive_sha256':sha(a),'recorded_delivery_sha256':delivery['archive_sha256'],'manifest_verification':d,'snapshot_sha256':sha(snapshot),'scope':'Full predecessor verified in this continuation; no new source recovery gap. Historical Core 8.3 loss remains recorded separately.','seconds':time.monotonic()-start}
assert r['archive_bytes']==delivery['archive_bytes'] and r['archive_sha256']==delivery['archive_sha256']
(R/'evidence/PREDECESSOR_AUTHENTICATION_BLOCK18.json').write_text(json.dumps(r,indent=2)+'\n')
shutil.copy2('/mnt/data/Machine_Native_Reasoning_Lean_Core24_Verification.json',R/'evidence/history17/DELIVERY_VERIFICATION.json')
s=importlib.util.spec_from_file_location('vf',R/'scripts/verify.py');vf=importlib.util.module_from_spec(s);s.loader.exec_module(vf)
new={'PositivePackets','CoordinatePackets','PacketTransport','PositivePacketExamples'}
inv=vf.source_inventory();sel=[r for r in inv if Path(r['file']).stem in new]
(R/'release/NEW_DECLARATIONS.json').write_text(json.dumps(sel,indent=2,ensure_ascii=False)+'\n')
module_rows=[]
for m in sorted(new):
 p=R/'MachineTheory'/f'{m}.lean';rows=[a for a in sel if Path(a['file']).stem==m]
 module_rows.append({'file':str(p.relative_to(R)),'sha256':sha(p),'lines':len(p.read_text().splitlines()),'authored_declarations':len(rows),'supporting_theorems':sum(a['kind'] in ['theorem','lemma'] for a in rows)})
(R/'release/NEW_MODULES.json').write_text(json.dumps(module_rows,indent=2)+'\n')
print('predecessor authenticated',d['payload_files'],'new supporting theorems',sum(r['supporting_theorems'] for r in module_rows))
print(module_rows)
