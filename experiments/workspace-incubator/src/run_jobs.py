"""Process supervisor. All children must finish before the research is delivered."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(planfile,output):
    jobs=json.loads(planfile.read_text());before={str(p.relative_to(ROOT)):sha(p) for sub in ('src','inputs','notes') for p in sorted((ROOT/sub).rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',NUMEXPR_NUM_THREADS='1',PYTHONHASHSEED='0')
    processes=[];records=[]
    for job in jobs:
        log=ROOT/job['log'];log.parent.mkdir(parents=True,exist_ok=True)
        stream=log.open('w');start=time.time();p=subprocess.Popen(job['argv'],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT)
        processes.append((p,stream,job,start));print('START',job['name'],p.pid,flush=True)
    while processes:
        remaining=[]
        for p,stream,job,start in processes:
            code=p.poll()
            if code is None:remaining.append((p,stream,job,start));continue
            stream.close();r=dict(job,returncode=code,pid=p.pid,started_at=start,finished_at=time.time(),elapsed_seconds=time.time()-start,log_sha256=sha(ROOT/job['log']));records.append(r)
            print('EXIT',job['name'],code,flush=True)
            output.write_text(json.dumps({'status':'RUNNING','records':records},indent=2))
        processes=remaining
        if processes:time.sleep(1)
    after={n:sha(ROOT/n) for n in before}
    output.write_text(json.dumps({'status':'COMPLETED' if all(r['returncode']==0 for r in records) else 'CHILD_FAILED','input_hashes_before':before,'input_hashes_after':after,'inputs_unchanged':before==after,'records':records},indent=2))
    if not all(r['returncode']==0 for r in records):raise SystemExit(1)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('plan',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.plan,a.output)
