#!/usr/bin/env python3
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import argparse, hashlib, json, re, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]; RD=ROOT/'results/v0.38.0/negative_all'; RD.mkdir(parents=True,exist_ok=True)
P=argparse.ArgumentParser(); P.add_argument('--seconds',type=int,default=60); P.add_argument('--workers',type=int,default=2); P.add_argument('--per-file-seconds',type=int,default=90); A=P.parse_args()
files=sorted((ROOT/'tests/negative').glob('*.lean'))
setup_rx=re.compile(r'object file .*does not exist|unknown module|failed to locate application|No such file or directory',re.I)
def valid(f):
    jp=RD/f'{f.stem}.json'; lp=RD/f'{f.stem}.log'
    if not jp.exists() or not lp.exists(): return False
    try:r=json.loads(jp.read_text())
    except Exception:return False
    txt=lp.read_text(errors='replace')
    return (r.get('source_sha256')==hashlib.sha256(f.read_bytes()).hexdigest() and r.get('returncode',0)!=0 and
            not r.get('timed_out',False) and not setup_rx.search(txt))
def run(f):
    log=RD/f'{f.stem}.log'
    return subprocess.call([sys.executable,str(ROOT/'tools/lean_one.py'),str(f.relative_to(ROOT)),'--no-output',
                            '--seconds',str(A.per_file_seconds),'--log',str(log.relative_to(ROOT))],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
done={f for f in files if valid(f)}; pending=[f for f in files if f not in done]; active={}; failed=[]; start=time.monotonic()
with ThreadPoolExecutor(max_workers=A.workers) as pool:
    while pending or active:
        while pending and len(active)<A.workers and time.monotonic()-start<A.seconds:
            f=pending.pop(0); active[pool.submit(run,f)]=f; print('START',f.name,flush=True)
        if not active: break
        finished,_=wait(active,return_when=FIRST_COMPLETED)
        for fut in finished:
            f=active.pop(fut)
            if valid(f): done.add(f); print('PASS',f.name,flush=True)
            else: failed.append(f); print('BAD',f.name,flush=True)
        if failed: break
records=[]
for f in files:
    jp=RD/f'{f.stem}.json'; lp=RD/f'{f.stem}.log'; ok=valid(f)
    rec=json.loads(jp.read_text()) if jp.exists() else {'returncode':None,'timed_out':False}
    rec.update(source=str(f.relative_to(ROOT)),expected_rejection=ok)
    records.append(rec)
summary={'total':len(files),'substantive_rejections':sum(r['expected_rejection'] for r in records),'records':records}
(RD/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('CURRENT',summary['substantive_rejections'],'/',summary['total'],'REMAINING',summary['total']-summary['substantive_rejections'],'FAILED',[f.name for f in failed],flush=True)
sys.exit(1 if failed else 0)
