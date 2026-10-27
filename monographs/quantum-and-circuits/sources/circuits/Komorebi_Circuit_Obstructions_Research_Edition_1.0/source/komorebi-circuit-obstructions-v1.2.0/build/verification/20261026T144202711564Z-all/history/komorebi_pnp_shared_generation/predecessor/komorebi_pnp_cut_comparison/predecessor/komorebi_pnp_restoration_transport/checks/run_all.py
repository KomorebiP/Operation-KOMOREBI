#!/usr/bin/env python3
"""Portable bounded runner with explicit hashes and historical replay boundary."""
from pathlib import Path
import hashlib,json,os,platform,subprocess,sys,time
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results';LOGS=ROOT/'logs'
RESULTS.mkdir(exist_ok=True);LOGS.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
inputs=[ROOT/'RESEARCH_NOTE.md',ROOT/'AUDIT.md',ROOT/'GAP_LEDGER.md',ROOT/'README.md',Path(__file__),
        ROOT/'checks/verify_restoration_transport.py',ROOT/'checks/verify_clique_endpoint.py',
        ROOT/'predecessor/komorebi_pnp_dirty_stable/checks/verify_dirty_stable.py',
        ROOT/'predecessor/komorebi_pnp_dirty_stable/results/verification.json']
before={str(p.relative_to(ROOT)):sha(p) for p in inputs}
manifest={'status':'RUNNING','started_utc':now(),'python':sys.version,'platform':platform.platform(),
 'domain':'exact Boolean functions, GF(2) linear algebra, integer graph certificates',
 'universal_proof_status':'written and self-reviewed, not formally verified',
 'inputs_before':before,'runs':[],
 'predecessor_archive_sha256':'9a27b285bb1970ddf9c2d77a8b6ea2ad84e41aa759a117ff487f10e2f8f451ad'}
source=inputs[-2].read_text();old="'/mnt/data/komorebi_pnp_dirty_stable/results/verification.json'"
assert source.count(old)==1
replay=RESULTS/'historical_replay_runtime.py'
replay.write_text(source.replace(old,repr(str(RESULTS/'predecessor_replay.json'))))
commands=[('predecessor_output_redirect_only',[sys.executable,str(replay)],35),
 ('restoration_transport',[sys.executable,str(ROOT/'checks/verify_restoration_transport.py')],40),
 ('clique_endpoint',[sys.executable,str(ROOT/'checks/verify_clique_endpoint.py')],40)]
try:
 for name,argv,limit in commands:
  start=time.perf_counter()
  p=subprocess.run(argv,cwd=ROOT,capture_output=True,text=True,timeout=limit)
  log=LOGS/(name+'_final.log');log.write_text(p.stdout+p.stderr)
  manifest['runs'].append({'name':name,'argv':argv,'timeout_seconds':limit,'exit_code':p.returncode,
                           'elapsed_seconds':time.perf_counter()-start,'log':str(log.relative_to(ROOT)),'log_sha256':sha(log)})
  if p.returncode:raise RuntimeError(f'{name} failed: {p.stderr[-1000:]}')
 assert json.loads((RESULTS/'predecessor_replay.json').read_text())==json.loads(inputs[-1].read_text())
 after={str(p.relative_to(ROOT)):sha(p) for p in inputs};assert before==after
 manifest['inputs_after']=after
 outputs=[RESULTS/'predecessor_replay.json',RESULTS/'verification.json',RESULTS/'clique_endpoint.json']
 manifest['outputs']={str(p.relative_to(ROOT)):sha(p) for p in outputs}
 manifest['status']='PASS'
except Exception as exc:
 manifest['status']='FAILED';manifest['failure']=repr(exc)
 raise
finally:
 manifest['finished_utc']=now();(RESULTS/'COMPUTATION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'runs':[(r['name'],r['elapsed_seconds']) for r in manifest['runs']]},indent=2))
