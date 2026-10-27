#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def source_hashes():
 return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for parent in ['checks','formalization','prior'] for p in (ROOT/parent).rglob('*') if p.is_file() and p.suffix in {'.py','.lean','.md'}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--runtime',required=True,type=Path);ap.add_argument('--part',choices=['all','core','high'],default='all');args=ap.parse_args()
 start=datetime.now(timezone.utc).isoformat();tic=time.perf_counter();before=source_hashes()
 tasks=[('lean',[sys.executable,'checks/run_lean.py','--runtime',str(args.runtime.resolve())],120),
        ('exact',[sys.executable,'checks/exact_checks.py'],40),
        ('numerical_50',[sys.executable,'checks/numerical_checks.py','--dps','50'],120),
        ('numerical_90',[sys.executable,'checks/numerical_checks.py','--dps','90'],150)]
 if args.part=='core':tasks=tasks[:3]
 if args.part=='high':tasks=tasks[3:]
 env=os.environ.copy();env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
 runs=[]
 for name,cmd,limit in tasks:
  t=time.perf_counter();p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=limit)
  (ROOT/'evidence'/f'{name}_run.log').write_text(p.stdout)
  runs.append({'name':name,'argv':cmd,'timeout_seconds':limit,'exit_status':p.returncode,'runtime_seconds':time.perf_counter()-t})
  print(p.stdout,end='',flush=True)
  if p.returncode:raise SystemExit(p.returncode)
 after=source_hashes()
 if before!=after:raise AssertionError('Source mutation during checks')
 out={'started_at':start,'runtime_seconds':time.perf_counter()-tic,'exit_status':0,'part':args.part,'runs':runs,'input_hashes_before':before,'input_hashes_after':after,'resources':'Separate synchronous subprocesses with specified timeouts. Lean -j1. Cooperative numeric thread caps. Environment cgroup memory maximum 4 GiB, not an additional per-process memory limiter.'}
 (ROOT/'evidence'/f'run_{args.part}.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
