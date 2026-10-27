from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,os
base=Path('/workspace/scratch/2e8d212e9ca7');r=base/'work11/Komorebi_LSM_Lean_0.10.0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rep=json.loads((r/'verification/block11_release_run/report.json').read_text())
assert rep['passed'] and rep['complete'],rep.get('failure','run incomplete')
assert len(rep['stages'])==243
assert not any(s['timed_out'] for s in rep['stages'])
subprocess.run(['python3','scripts/check_metadata.py','--out','verification/block11_metadata.json'],cwd=r,check=True)
meta=json.loads((r/'verification/block11_metadata.json').read_text());assert meta['passed']
attempts=[json.loads(p.read_text()) for p in sorted((r/'verification/development_block11').glob('*.json'))]
summary={'invocations':len(attempts),'successful':sum(x['returncode']==0 for x in attempts),'failed':sum(x['returncode']!=0 for x in attempts),'scope':'Compiler development only, not release theorem or rejection counts. Source snapshots and diagnostics retained. Deterministic Lean heartbeat-limit errors count as failures, not subprocess timeouts.'}
(r/'verification/BLOCK11_DEVELOPMENT_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
p=json.loads((r/'PROGRESS.json').read_text());p['source_verification']={'passed':True,'complete':True,'stages':243,'report':'verification/block11_release_run/report.json','metadata_checks':meta['record_count']};p['development_attempts']=summary
(r/'PROGRESS.json').write_text(json.dumps(p,indent=2)+'\n')
card=json.loads((r/'verification/BLOCK11_CLAIM_CARD.json').read_text());card['kernel_evidence']='Stable source passed 243 stages. P33 and P34 complete under the documented conventions; P32 remains partial. See external delivery verification for the exact ZIP.'
(r/'verification/BLOCK11_CLAIM_CARD.json').write_text(json.dumps(card,indent=2)+'\n')
s=(r/'AUDIT.md').read_text().replace('P33 and P34 have complete formal proof candidates','P33 and P34 have complete kernel-checked formal proofs').replace('Current acceptance: pending cumulative verification.','Current source acceptance: all 243 stages passed. Exact-ZIP fresh-run acceptance is recorded separately.').replace('Development compile passed','Passed: compile, axiom audit and kernel replay').replace('| Full cumulative and fresh ZIP verification | Separate reports | Pending |','| Full cumulative source verification | 243 stages, 80 metadata checks | Passed |\n| Exact ZIP fresh extraction and verification | External delivery JSON | Consult actual report |')
s+='\nAccepted source evidence: 83 compilation targets, one executable-example stage, one declaration-axiom stage, 82 kernel replays and 76 expected proof rejections. All 1,338 declaration records were audited; only propext, Classical.choice and Quot.sound are allowed. No subprocess timeout occurred. P32 is still incomplete despite all implemented proof modules passing.\n'
(r/'AUDIT.md').write_text(s)
p=r/'PROGRESS.md';s=p.read_text().replace('P33 and P34 are newly complete proof candidates, pending cumulative acceptance.','P33 and P34 are newly complete, with cumulative source acceptance.');s+=f"\nSource verification: PASS, 243 stages. Metadata: PASS, {meta['record_count']} checks. Development: {summary['invocations']} invocations, {summary['successful']} successful and {summary['failed']} failed. The exact delivered archive has a separate fresh-run report.\n";p.write_text(s)
shutil.copy2(__file__,r/'verification/development_tools/finalize11.py')
out=base/'deliverables11';out.mkdir(exist_ok=True);stage=out/'Komorebi_LSM_Lean_0.11.0';assert not stage.exists()
shutil.copytree(r,stage,ignore=shutil.ignore_patterns('.build','__pycache__','*.pyc','MANIFEST.json'))
files={str(p.relative_to(stage)):{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(stage.rglob('*')) if p.is_file()}
(stage/'MANIFEST.json').write_text(json.dumps({'release':'0.11.0','theory':'1.0.0','kind':'source_and_verification','files':files},indent=2)+'\n')
subprocess.run(['python3','scripts/verify_hashes.py'],cwd=stage,check=True)
archive=out/'Komorebi_Large_Signal_Model_Lean_0.11.0.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(stage.rglob('*')):
  if p.is_file():z.write(p,str(p.relative_to(out)))
receipt={'release':'0.11.0','archive':archive.name,'sha256':sha(archive),'bytes':archive.stat().st_size,'inventory_count':len(files)+1,'source_candidate_passed':True,'source_candidate_report_sha256':sha(r/'verification/block11_release_run/report.json'),'fresh_extraction_passed':False,'complete':False,'metadata_checks':meta['record_count'],'development':summary,'coverage':{'complete':38,'partial':[32],'not_formalized':48,'frozen_total':87}}
(out/'delivery_block11_pending.json').write_text(json.dumps(receipt,indent=2)+'\n')
fresh=base/'fresh11';fresh.mkdir(exist_ok=True)
with zipfile.ZipFile(archive) as z:z.extractall(fresh)
fr=fresh/stage.name;setup=[]
for cmd in [['python3','scripts/verify_hashes.py'],['python3','scripts/build_inventory.py'],['python3','scripts/check_metadata.py']]:
 p=subprocess.run(cmd,cwd=fr,capture_output=True,text=True);setup.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,setup[-1]
receipt['setup_stages']=setup;receipt['project_objects_absent_before_replay']=not (fr/'.build').exists()
(out/'delivery_block11_pending.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in ['development','setup_stages']},indent=2),flush=True)
kit=base/'runtime11/Komorebi_Portable_Lean_4.34.0-rc2';env=os.environ.copy();env['LD_PRELOAD']=str(kit/'compat/app_path.so')
with (out/'fresh_block11_driver.log').open('w') as log:
 p=subprocess.run(['python3','scripts/verify.py','--kit',str(kit),'--out',str(out/'fresh_block11_run')],cwd=fr,env=env,stdout=log,stderr=subprocess.STDOUT)
freshrep=json.loads((out/'fresh_block11_run/report.json').read_text());receipt.update(fresh_extraction_passed=freshrep['passed'],complete=freshrep['complete'],passed=freshrep['passed'] and freshrep['complete'] and p.returncode==0,fresh_run=freshrep)
(out/'Komorebi_Large_Signal_Model_Lean_0.11.0_Verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert receipt['passed'],freshrep.get('failure')
assert len(freshrep['stages'])==243
for name,src in [('Guide.md','LEAN_GUIDE.md'),('Progress.md','PROGRESS.md'),('Audit.md','AUDIT.md'),('Coverage.json','COVERAGE.json')]:shutil.copy2(stage/src,out/('Komorebi_Large_Signal_Model_Lean_0.11.0_'+name))
print('DELIVERY PASS',flush=True)
