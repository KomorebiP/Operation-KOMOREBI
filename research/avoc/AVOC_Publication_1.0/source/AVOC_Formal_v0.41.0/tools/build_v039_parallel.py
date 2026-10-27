#!/usr/bin/env python3
"""Bounded dependency-aware local v0.39 rebuild; external caches remain unchanged."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import argparse,hashlib,json,re,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]; RD=ROOT/'results/v0.39.0'
P=argparse.ArgumentParser();P.add_argument('--seconds',type=int,default=60);P.add_argument('--workers',type=int,default=3);P.add_argument('--per-target-seconds',type=int,default=180);A=P.parse_args()
order=json.loads((RD/'build_order.json').read_text()); bymod={str(Path(f).with_suffix('')).replace('/','.'):f for f in order}
deps={f:{bymod[d] for d in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',(ROOT/f).read_text(),re.M)} for f in order}
def ready(f):
    p=RD/f'clean_{Path(f).stem}.json'; o=ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
    if not p.exists() or not o.exists(): return False
    r=json.loads(p.read_text()); current={}
    for d in deps[f]:
        op=ROOT/'.lake/build/lib/lean'/Path(d).with_suffix('.olean'); name=str(Path(d).with_suffix('')).replace('/','.')
        current[name]=hashlib.sha256(op.read_bytes()).hexdigest() if op.exists() else None
    return (r.get('returncode')==0 and not r.get('timed_out',False) and r.get('imports_unchanged',False) and
            r.get('import_outputs')==current and r.get('source_sha256')==hashlib.sha256((ROOT/f).read_bytes()).hexdigest() and
            r.get('output_sha256')==hashlib.sha256(o.read_bytes()).hexdigest())
done={f for f in order if ready(f)}
while True:
    bad={f for f in done if not deps[f] <= done}
    if not bad: break
    done-=bad
pending=set(order)-done; active={}; failed=[]; start=time.monotonic()
def run(f):
    log=f'results/v0.39.0/clean_{Path(f).stem}.log'
    return subprocess.call([sys.executable,str(ROOT/'tools/lean_one.py'),f,'--seconds',str(A.per_target_seconds),'--log',log],stdout=subprocess.DEVNULL)
with ThreadPoolExecutor(max_workers=A.workers) as pool:
    while pending or active:
        if time.monotonic()-start<A.seconds:
            for f in order:
                if len(active)>=A.workers:break
                if f in pending and deps[f]<=done:
                    pending.remove(f);active[pool.submit(run,f)]=f;print('START',f,flush=True)
        if not active:break
        finished,_=wait(active,return_when=FIRST_COMPLETED)
        for t in finished:
            f=active.pop(t)
            if t.result()==0: done.add(f);print('PASS',f,flush=True)
            else: failed.append(f);print('FAIL',f,(RD/f'clean_{Path(f).stem}.log').read_text(errors='replace')[-3000:],flush=True)
        if failed:break
print('CURRENT',len(done),'/',len(order),'REMAINING',len(pending),'FAILED',failed,flush=True)
sys.exit(1 if failed else 0)
