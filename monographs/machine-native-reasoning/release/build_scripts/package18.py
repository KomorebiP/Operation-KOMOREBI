"""Seal full and compact current-source packages and verify both clean extractions."""
from pathlib import Path, PurePosixPath
import argparse,datetime,hashlib,importlib.util,json,os,shutil,stat,sys,tempfile,zipfile
sys.dont_write_bytecode=True
R=Path('/mnt/data/Machine_Native_Reasoning_Lean_Core25');OUT=Path('/mnt/data')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as s:
  for b in iter(lambda:s.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def load(p):return json.loads(p.read_text())
spec=importlib.util.spec_from_file_location('integrity18',R/'tools/verify_package.py');vp=importlib.util.module_from_spec(spec);spec.loader.exec_module(vp)
def canonical(n):
 p=PurePosixPath(n)
 if p.is_absolute() or any(c in ('','.','..') for c in n.split('/')) or '\\' in n or ':' in n or any(ord(c)<32 for c in n):raise ValueError(n)
 return p

def package(flavor):
 admission=load(R/'release/ADMISSION_RECORD.json');assert admission['status']=='PASS'
 pins=load(R/'evidence/final18/report.json')['input_sha256_after']
 stage_parent=Path('/mnt/data/core25/delivery_'+flavor)
 if stage_parent.exists():raise FileExistsError(stage_parent)
 stage=stage_parent/'Machine_Native_Reasoning_Lean_Core25';stage.mkdir(parents=True)
 omitted=[]
 for p in sorted(R.rglob('*')):
  if p.is_symlink():raise ValueError(f'Symlink in owned tree: {p}')
  if not p.is_file():continue
  rel=p.relative_to(R)
  if p.suffix.lower() in ['.ttf','.otf','.woff','.woff2']:raise ValueError(f'Standalone font excluded: {p}')
  omit='__pycache__' in rel.parts or p.suffix=='.pyc' or rel.as_posix()=='MANIFEST.json'
  if flavor=='compact' and p.suffix in ['.olean','.ilean','.o','.c']:omit=True
  if omit:
   omitted.append({'path':rel.as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'reason':'regenerable local cache' if '__pycache__' in rel.parts or p.suffix=='.pyc' else 'compiled object absent from compact source-and-receipts package'})
   continue
  q=stage/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 # Keep the original predecessor as bytes, not an invented reconstructed history.
 prior=OUT/('Machine_Native_Reasoning_Lean_Core24_v0.17.1.zip' if flavor=='full' else 'Machine_Native_Reasoning_Lean_Core24_Source_and_Receipts.zip')
 target=stage/'evidence/history17'/prior.name;shutil.copy2(prior,target)
 archive_layout=f'''# Archive layout — {flavor}

This package contains the complete current formal source, original reviewed-core
source/PDF, source correspondence, all current controls and exact checkers, both
successful cumulative execution records, the separately extracted-source comparison,
all new development proof attempts, recovery receipts and portable reproduction tools.

{'Current compiled project objects are retained. The complete intact predecessor archive is preserved as its original ZIP stream.' if flavor=='full' else 'Current compiled project objects are omitted. The predecessor source-and-receipts ZIP is preserved unchanged; the full prior failed-run/object history remains in its separately delivered complete archive.'}

The original predecessor file is `evidence/history17/{prior.name}`, with
SHA-256 `{sha(prior)}`. It is historical evidence, not a new run on changed source.
The prior Core 8.3 missing-payload notice remains historical. Current source recovery
has no missing input. The compact distribution retains every one of the {len(pins)}
current proof-gate inputs and every current successful command log, but reproducing
old object comparisons locally requires rebuilding objects or the full package.

No runtime or standalone font binaries are shipped. The large pinned runtime is an
external prerequisite. Local Python bytecode caches are omitted and inventoried.
`MANIFEST.json` describes exactly this distribution and excludes only itself.
The external delivery JSON records the final ZIP hash, avoiding a circular hash.
`tools/verify_package.py` is the current strict package verifier. The older retained
`scripts/verify_release.py` expects a historical SHA256SUMS format and is not the
entry point for this distribution.

Root source-bound metadata retains its preparation wording. The accepted verdict
is in `release/ADMISSION_RECORD.json`, `release/REPORT.md` and
`release/ACCEPTED_PROGRESS_LEDGER.md`. Rebuilding the book or changing any source
requires a new verification record, not reuse of old PASS labels.
'''
 (stage/'release/ARCHIVE_LAYOUT.md').write_text(archive_layout)
 (stage/'release/OMITTED_LOCAL_FILES.json').write_text(json.dumps(omitted,indent=2)+'\n')
 (stage/'START_HERE.txt').write_text(f'''MACHINE-NATIVE REASONING — CORE 2.5 — 0.18.0
Accepted selected-core correspondence: 26/27.
Distribution: {flavor}.

Read release/REPORT.md, release/PROOF_GUIDE.md and
release/ACCEPTED_PROGRESS_LEDGER.md first. The next selected result is Core 3.2.

Before creating build outputs:
    python tools/verify_package.py

For a fresh complete local replay using the pinned offline runtime:
    python scripts/supervise.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay --whole-timeout 1800

See release/RUNTIME_REPRODUCTION.md for restoration of the saved five runtime parts.
See release/ARCHIVE_LAYOUT.md for exact inclusions and historical evidence limits.
The original book is not rebuilt, and the entire monograph is not claimed formalized.
''')
 assert all((stage/n).is_file() and sha(stage/n)==h for n,h in pins.items())
 entries=[{'path':p.relative_to(stage).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(stage.rglob('*')) if p.is_file()]
 (stage/'MANIFEST.json').write_text(json.dumps({'schema':vp.SCHEMA,'version':'0.18.0','flavor':flavor,'files':entries},indent=2)+'\n')
 staged=vp.verify(stage)
 basename='Machine_Native_Reasoning_Lean_Core25_v0.18.0.zip' if flavor=='full' else 'Machine_Native_Reasoning_Lean_Core25_Source_and_Receipts.zip'
 zpath=OUT/basename
 if zpath.exists():raise FileExistsError(zpath)
 with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
  for p in sorted(stage.rglob('*')):
   if p.is_file():z.write(p,stage.name+'/'+p.relative_to(stage).as_posix())
 with tempfile.TemporaryDirectory(prefix='core25_clean_',dir='/mnt/data/core25') as tmp:
  with zipfile.ZipFile(zpath) as z:
   if z.testzip() is not None:raise ValueError('ZIP CRC failure')
   names=z.namelist()
   if len(names)!=len(set(names)):raise ValueError('Duplicate members')
   for info in z.infolist():
    p=canonical(info.filename)
    if p.parts[0]!=stage.name:raise ValueError('Unexpected archive root')
    if stat.S_ISLNK(info.external_attr>>16):raise ValueError('ZIP symlink')
   z.extractall(tmp)
  fresh=Path(tmp)/stage.name
  extracted=vp.verify(fresh)
  assert all(sha(fresh/n)==h for n,h in pins.items())
  assert (fresh/'evidence/history17'/prior.name).read_bytes()==prior.read_bytes()
  for name in ['ADMISSION_RECORD.json','REPORT.md','PROOF_GUIDE.md','ACCEPTED_PROGRESS_LEDGER.md']:
   assert (fresh/'release'/name).read_bytes()==(R/'release'/name).read_bytes()
 record={'schema':'komorebi.machine_reasoning.core25.delivery.v1','status':'PASS','version':'0.18.0','flavor':flavor,'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'archive':basename,'archive_bytes':zpath.stat().st_size,'archive_sha256':sha(zpath),'manifest_payload_files':len(entries),'zip_members':len(names),'clean_extraction_verified':True,'staged_integrity':staged,'extracted_integrity':extracted,'source_inputs_match_actual_gates':len(pins),'preserved_predecessor_archive':{'name':prior.name,'bytes':prior.stat().st_size,'sha256':sha(prior)},'omitted_local_files':len(omitted),'standalone_documents':{p.name:sha(p) for p in [OUT/'Machine_Native_Reasoning_Lean_Core25_Report.md',OUT/'Machine_Native_Reasoning_Lean_Core25_Proof_Guide.md',OUT/'Machine_Native_Reasoning_Lean_Core25_Progress_Ledger.md']},'admission':admission}
 receipt=OUT/('Machine_Native_Reasoning_Lean_Core25_Verification.json' if flavor=='full' else 'Machine_Native_Reasoning_Lean_Core25_Compact_Verification.json')
 receipt.write_text(json.dumps(record,indent=2)+'\n')
 (OUT/(basename+'.sha256')).write_text(record['archive_sha256']+'  '+basename+'\n')
 print(json.dumps({k:record[k] for k in ['flavor','archive','archive_bytes','archive_sha256','manifest_payload_files','zip_members','source_inputs_match_actual_gates']},indent=2),flush=True)
 return record

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--flavor',choices=['full','compact','both'],default='both');a=p.parse_args()
 for f in ['full','compact'] if a.flavor=='both' else [a.flavor]:package(f)
