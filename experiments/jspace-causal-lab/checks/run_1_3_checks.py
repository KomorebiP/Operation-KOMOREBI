"""Capture actual return codes and source hashes for the release check sequence."""
from pathlib import Path
import subprocess, json, time, hashlib, datetime, os
ROOT=Path(__file__).resolve().parents[1]
commands=[['node','checks/test_port.js'],['node','checks/test_causal_port.js'],['node','checks/test_refine_engine.js'],['node','checks/test_challenge_engine.js'],['python','checks/check_challenge_pytorch.py'],['python','checks/audit_challenge_results.py'],['python','checks/test_challenge_browser.py'],['python','checks/test_challenge_browser_numeric.py'],['python','checks/test_legacy_browser_on_1_3.py'],['python','rebuild.py']]
files=sorted(p for folder in ['app','runtime'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p.relative_to(ROOT)):hashfile(p) for p in files}
start=time.monotonic();started=datetime.datetime.now(datetime.timezone.utc).isoformat();rows=[]
for i,argv in enumerate(commands):
 t=time.monotonic();r=subprocess.run(argv,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90,env={**os.environ,'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
 name=f'checks/robustness/release_check_{i:02d}.log';(ROOT/name).write_text(r.stdout+'\nSTDERR\n'+r.stderr)
 rows.append({'argv':argv,'returncode':r.returncode,'elapsed_seconds':time.monotonic()-t,'log':name,'log_sha256':hashfile(ROOT/name)})
 if r.returncode:break
out={'status':'PASS' if all(x['returncode']==0 for x in rows) and len(rows)==len(commands) else 'FAIL','started_at':started,'elapsed_seconds':time.monotonic()-start,'commands':rows,'source_hashes_before':before,'source_hashes_after':{str(p.relative_to(ROOT)):hashfile(p) for p in files},'limits':{'per_command_timeout_seconds':90,'torch_threads_in_numeric_script':1,'thread_environment':'cooperative OMP/MKL cap, not an OS CPU quota'}}
assert out['source_hashes_before']==out['source_hashes_after']
(ROOT/'checks/robustness/release_execution.json').write_text(json.dumps(out,indent=2));print(json.dumps({'status':out['status'],'commands':len(rows),'seconds':out['elapsed_seconds']}))
if out['status']!='PASS':raise SystemExit(1)
