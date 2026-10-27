"""Portable sequential replay with separate logs and source hashes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess, sys, time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
GROUPS=['structural','signed_noncentral','interval','accuracy','verified_spectrum','directed_contract']
p=argparse.ArgumentParser()
p.add_argument('--group',choices=GROUPS,action='append')
p.add_argument('--include-controls',action='store_true')
p.add_argument('--timeout',type=float,default=900)
p.add_argument('--output',type=Path)
args=p.parse_args()
out=args.output or HERE/('replay_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
out.mkdir(parents=True,exist_ok=False)
def hashes():
 return {str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((ROOT/'engine').glob('*.py'))}
before=hashes()
env=os.environ.copy()
env['PYTHONDONTWRITEBYTECODE']='1'
for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:env[name]='1'
records=[]
jobs=[(group,[sys.executable,str(HERE/'run_suite.py'),group,str(out/(group+'_result.json'))]) for group in (args.group or GROUPS)]
if args.include_controls:jobs.append(('fresh_controls',[sys.executable,str(HERE/'fresh_controls.py'),str(out/'controls.json')]))
for name,command in jobs:
 start=time.perf_counter()
 try:
  with (out/(name+'_stdout.txt')).open('wb') as stdout,(out/(name+'_stderr.txt')).open('wb') as stderr:
   result=subprocess.run(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr,timeout=args.timeout)
  status='completed' if result.returncode==0 else 'failed';exit_code=result.returncode
 except subprocess.TimeoutExpired:status='timeout';exit_code=None
 record={'group':name,'actual_argv':command,'status':status,'exit_code':exit_code,'elapsed_seconds':time.perf_counter()-start,'timeout_seconds':args.timeout}
 records.append(record);print(name,status,flush=True)
after=hashes()
record={'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'runs':records,'source_hashes_before':before,'source_hashes_after':after,'sources_unchanged':before==after,'python':sys.version,'thread_caps':'common numerical-library thread environment values set to1; cooperative, not an enforced CPU/memory cap','non_claim':'Passing replay tests is finite computational evidence, not a general theorem or proof of interval-library correctness.'}
(out/'replay_status.json').write_text(json.dumps(record,indent=2)+'\n')
raise SystemExit(0 if before==after and all(r['status']=='completed' for r in records) else 1)
