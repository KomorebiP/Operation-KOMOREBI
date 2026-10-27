"""Run the accepted test route with logs and before/after source fingerprints.
The separately blocked file:// assay is retained, not recategorized as passed.
"""
from pathlib import Path
import datetime,hashlib,json,os,platform,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[p for folder in ['app','runtime'] for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc']
inputs.extend([ROOT/'rebuild.py',ROOT/'checks/test_refine_engine.js',ROOT/'checks/test_refine_browser.py',ROOT/'checks/check_refine_pytorch.py'])
before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
commands=[['node','checks/test_port.js'],['node','checks/test_causal_port.js'],['node','checks/test_refine_engine.js'],['node','checks/make_refine_numeric_fixtures.js'],[sys.executable,'checks/check_refine_pytorch.py'],[sys.executable,'checks/audit_causal_results.py'],[sys.executable,'rebuild.py'],[sys.executable,'checks/test_causal_browser.py'],[sys.executable,'checks/test_refine_browser.py']]
start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();records=[]
for i,cmd in enumerate(commands):
 a=time.monotonic();r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=60)
 log=ROOT/'checks/logs'/f'refine_{i:02d}.log';log.write_text(r.stdout+'\nSTDERR\n'+r.stderr)
 records.append({'argv':cmd,'returncode':r.returncode,'seconds':time.monotonic()-a,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log)})
 print(json.dumps(records[-1]),flush=True)
 if r.returncode:raise SystemExit(r.returncode)
after={str(p.relative_to(ROOT)):sha(p) for p in inputs};assert before==after
import numpy,torch
out={'status':'PASS','started_at_utc':start,'seconds':time.monotonic()-t,'commands':records,'source_inputs_sha256':before,'source_unchanged':before==after,
 'environment':{'python':platform.python_version(),'platform':platform.platform(),'torch':torch.__version__,'numpy':numpy.__version__,'node':subprocess.check_output(['node','--version'],text=True).strip(),'chromium':subprocess.check_output(['/usr/bin/chromium','--version'],text=True).strip(),'cpu_affinity_count':len(os.sched_getaffinity(0))},
 'limits':['One 60-second timeout per subprocess, not a universal resource guarantee.','Separate direct file:// attempt was blocked by browser policy.','No training; finite engineering tests only.']}
(ROOT/'checks/REFINEMENT_EXECUTION.json').write_text(json.dumps(out,indent=2))
