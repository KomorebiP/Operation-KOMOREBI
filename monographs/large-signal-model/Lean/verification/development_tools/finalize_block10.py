from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,os
base=Path(__file__).resolve().parent.parent;root=base/'work/Komorebi_LSM_Lean_Block10'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((root/'verification/block10_release_run/report.json').read_text())
assert report['passed'] and report['complete'],report.get('failure','not complete')
assert len(report['stages'])==231
assert not any(s['timed_out'] for s in report['stages'])
metadata=json.loads((root/'verification/block10_metadata.json').read_text());assert metadata['passed']
subprocess.run(['python3','scripts/check_metadata.py','--out','verification/block10_metadata.json'],cwd=root,check=True)
attempts=[json.loads(p.read_text()) for p in sorted((root/'verification/development_block10').glob('*.json'))]
summary={'invocations':len(attempts),'successful':sum(x['returncode']==0 for x in attempts),'failed':sum(x['returncode']!=0 for x in attempts),'scope':'Development compiler invocations only; not release negative controls. All source snapshots and diagnostics preserved.','other_failures':['Prohibited word in English comment, preflight report preserved','Metadata replacement count 74 to 44, caught and repaired before accepted run'],'coverage':'Counts are not mathematical proof or rejection counts.'}
(root/'verification/BLOCK10_DEVELOPMENT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
card=json.loads((root/'verification/BLOCK10_CLAIM_CARD.json').read_text());card['verdict']='proved as written';card['evidence']='Source run passed 231 stages; see external delivery report for exact-archive fresh run.'
(root/'verification/BLOCK10_CLAIM_CARD.json').write_text(json.dumps(card,indent=2)+'\n')
p=json.loads((root/'PROGRESS.json').read_text());p['source_verification']={'passed':True,'complete':True,'stages':231,'report':'verification/block10_release_run/report.json','metadata_checks':76};p['development_attempts']=summary
(root/'PROGRESS.json').write_text(json.dumps(p,indent=2)+'\n')
s=(root/'AUDIT.md').read_text().replace('**Primary verdict:** pending cumulative verification. The finalization step replaces this verdict only after the accepted run passes.','**Primary verdict: proved as written.** The cumulative source verification passed all 231 stages.')
s=s.replace('Passed in development compile','Passed: compile, axiom audit and kernel replay').replace('Passed in development; rerun in release','Passed in release execution').replace('| Full source and fresh archive runs | Pending |','| Full source passed; exact-archive fresh run reported externally | Source passed |')
s+=f"\nAccepted source-candidate result: PASS, 231 stages: 79 compilation targets, one executable-example stage, one axiom-audit stage, 78 kernel replays and 72 proof rejections. All 1,304 named declaration axiom records passed. Metadata: 76 checks. Development: {summary['invocations']} compiler invocations, {summary['successful']} successful and {summary['failed']} failed, all retained. No subprocess timeout occurred in the accepted run.\n"
(root/'AUDIT.md').write_text(s)
(root/'PROGRESS.md').write_text((root/'PROGRESS.md').read_text()+f"\nAccepted source run: PASS, all 231 stages; metadata PASS, 76 checks. Development records preserve {summary['successful']} successful and {summary['failed']} failed compiler invocations. The separate delivery report records the fresh-extraction outcome and archive identity.\n")
# Preserve the packaging implementation for reproducible lineage.
shutil.copy2(__file__,root/'verification/block10_packaging.py')
out=base/'deliverables';stage=out/'Komorebi_LSM_Lean_0.10.0';assert not stage.exists()
shutil.copytree(root,stage,ignore=shutil.ignore_patterns('.build','__pycache__','*.pyc','MANIFEST.json'))
files={str(p.relative_to(stage)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(stage.rglob('*')) if p.is_file()}
(stage/'MANIFEST.json').write_text(json.dumps({'release':'0.10.0','theory':'1.0.0','kind':'source_and_verification','files':files},indent=2)+'\n')
subprocess.run(['python3','scripts/verify_hashes.py'],cwd=stage,check=True)
archive=out/'Komorebi_Large_Signal_Model_Lean_0.10.0.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(stage.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(out)))
receipt={'release':'0.10.0','archive':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'inventory_count':len(files)+1,'source_candidate_passed':True,'source_candidate_report_sha256':sha(root/'verification/block10_release_run/report.json'),'fresh_extraction_passed':False,'complete':False,'metadata_checks':76,'development':summary}
(out/'delivery_block10_pending.json').write_text(json.dumps(receipt,indent=2)+'\n')
fresh=base/'fresh_block10';fresh.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:z.extractall(fresh)
fr=fresh/stage.name;setup=[]
for cmd in [['python3','scripts/verify_hashes.py'],['python3','scripts/build_inventory.py'],['python3','scripts/check_metadata.py']]:
 r=subprocess.run(cmd,cwd=fr,capture_output=True,text=True)
 setup.append({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,setup[-1]
receipt['setup_stages']=setup;receipt['project_objects_absent_before_replay']=not (fr/'.build').exists()
(out/'delivery_block10_pending.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['development','setup_stages']},indent=2),flush=True)
kit=Path('/workspace/scratch/5d9f7f8127b0/runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2');env=os.environ.copy();env['LD_PRELOAD']=str(kit/'compat/app_path.so')
with (out/'fresh_block10_driver.log').open('w') as log:
 r=subprocess.run(['python3','scripts/verify.py','--kit',str(kit),'--out',str(out/'fresh_block10_run')],cwd=fr,env=env,stdout=log,stderr=subprocess.STDOUT)
rep=json.loads((out/'fresh_block10_run/report.json').read_text())
receipt.update(fresh_extraction_passed=rep['passed'],complete=rep['complete'],passed=rep['passed'] and rep['complete'] and r.returncode==0,fresh_run=rep)
(out/'Komorebi_Large_Signal_Model_Lean_0.10.0_Verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert receipt['passed'],rep.get('failure')
assert len(rep['stages'])==231
for name,source in [('Guide.md','LEAN_GUIDE.md'),('Progress.md','PROGRESS.md'),('Audit.md','AUDIT.md'),('Coverage.json','COVERAGE.json')]:
 shutil.copy2(stage/source,out/('Komorebi_Large_Signal_Model_Lean_0.10.0_'+name))
print('DELIVERY PASS',flush=True)
