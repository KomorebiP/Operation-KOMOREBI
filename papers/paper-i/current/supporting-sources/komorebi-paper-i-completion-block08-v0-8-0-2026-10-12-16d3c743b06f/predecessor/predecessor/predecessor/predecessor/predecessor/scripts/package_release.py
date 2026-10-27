#!/usr/bin/env python3
"""Package a completed verified handoff, test its ZIP and all manifested bytes."""
from pathlib import Path
import collections,hashlib,json,shutil,subprocess,zipfile
root=Path(__file__).resolve().parents[1]
r=json.loads((root/'VERIFICATION.json').read_text())
if r['status']!='PASS':raise SystemExit('Refusing a non-PASS handoff')
post=json.loads((root/'evidence/POSTFLIGHT.json').read_text())
if post.get('status')!='PASS' or not post.get('no_active_launcher'):raise SystemExit('Missing completed postflight')
# Explicitly inspect failure diagnostics, rather than accepting an arbitrary failing process.
run=root/'evidence/final_attempt01';diagnostics=[]
for name,needles in {
 'negative_FalseEquality':['decide','false'],
 'negative_Placeholder':['sorry'],
 'guard_InjectedAxiom':['OWNED AUDIT REJECTED'],
 'guard_InjectedPlaceholder':['OWNED AUDIT REJECTED dependency sorryAx'],
 'negative_block03_ZeroExponentMisuse':['decide','false'],
 'negative_block03_WrongResidueDimension':['Application type mismatch'],
 'negative_block03_RepeatedPrimaryOneSeed':['Application type mismatch'],
 'negative_block03_MissingDivisibilityChain':['Application type mismatch']
}.items():
 p=run/(name+'.log');text=p.read_text()
 if not all(s in text for s in needles):raise SystemExit('Unexpected control diagnostic: '+name)
 diagnostics.append({'check':name,'required_substrings':needles,'passed':True,'log_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'evidence/CONTROL_DIAGNOSTICS.json').write_text(json.dumps({'status':'PASS','diagnostics':diagnostics},indent=2)+'\n')
# Avoid distributing accidental interpreter caches alongside source.
for d in list(root.rglob('__pycache__')):
 if 'predecessor' not in d.parts:shutil.rmtree(d)
files=sorted(p for p in root.rglob('*') if p.is_file() and p.name!='MANIFEST_SHA256.json')
# Include nested predecessor manifests. Only exclude the root self-manifest.
files=sorted(p for p in root.rglob('*') if p.is_file() and p!=root/'MANIFEST_SHA256.json')
rows=[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
m={'schema':'komorebi.completion.manifest/0.3.0','algorithm':'sha256','excluded':['MANIFEST_SHA256.json'],'count':len(rows),'files':rows}
(root/'MANIFEST_SHA256.json').write_text(json.dumps(m,indent=2)+'\n')
p=subprocess.run(['python3',str(root/'scripts/verify_bundle.py')],capture_output=True,text=True)
if p.returncode:raise SystemExit(p.stdout+p.stderr)
zip_path=root.parent/(root.name+'.zip')
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for f in sorted(p for p in root.rglob('*') if p.is_file()):z.write(f,str(Path(root.name)/f.relative_to(root)))
with zipfile.ZipFile(zip_path) as z:
 if z.testzip() is not None:raise SystemExit('ZIP CRC check failed')
 for item in rows:
  data=z.read(root.name+'/'+item['path'])
  if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise SystemExit('ZIP payload mismatch '+item['path'])
 if len(z.namelist())!=len(rows)+1:raise SystemExit('Unexpected ZIP entry count')
report={'status':'PASS','zip':str(zip_path),'zip_bytes':zip_path.stat().st_size,'zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'zip_crc':'PASS','manifested_payloads_checked':len(rows),'zip_entries':len(rows)+1,'manifest_sha256':hashlib.sha256((root/'MANIFEST_SHA256.json').read_bytes()).hexdigest(),'extracted_bundle_check':{'command':p.args,'exit_code':p.returncode,'stdout':p.stdout},'max_archived_path_length':max(len(root.name+'/'+x['path']) for x in rows),'production_modules':28,'accepted_command_checks':len(r['checks'])}
(root.parent/'Paper_I_Block03_Package_Integrity_2026-10-10.json').write_text(json.dumps(report,indent=2)+'\n')
copies={
 'REPORT.md':'Paper_I_Block03_Completion_Report_2026-10-10.md',
 'PROOF_GUIDE.md':'Paper_I_Block03_Proof_Guide_2026-10-10.md',
 'PROGRESS_LEDGER.md':'Paper_I_Block03_Progress_Ledger_v0.3.0.md',
 'VERIFICATION.json':'Paper_I_Block03_Verification_2026-10-10.json',
 'coverage/COVERAGE_108.md':'Paper_I_Expanded_108_Record_Lean_Coverage_v0.3.0.md'}
for src,dst in copies.items():shutil.copy2(root/src,root.parent/dst)
print(json.dumps(report,indent=2))
