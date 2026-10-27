#!/usr/bin/env python3
"""Bounded dependency-aware local rebuild. External caches remain unchanged."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
import json,re,subprocess,sys,time,hashlib,argparse
root=Path(__file__).resolve().parents[1]; rd=root/'results/v0.28.0'
a=argparse.ArgumentParser();a.add_argument('--seconds',type=int,default=60);a.add_argument('--workers',type=int,default=3);ns=a.parse_args()
order=json.loads((rd/'build_order.json').read_text()); bymod={str(Path(f).with_suffix('')).replace('/','.'):f for f in order}
deps={f:{bymod[d] for d in re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',(root/f).read_text(),re.M)} for f in order}
def readyfile(f):
 p=rd/('clean_'+Path(f).stem+'.json');o=root/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
 if not p.exists() or not o.exists():return False
 r=json.loads(p.read_text())
 current={}
 for d in deps[f]:
  depout=root/'.lake/build/lib/lean'/Path(d).with_suffix('.olean')
  name=str(Path(d).with_suffix('')).replace('/','.')
  current[name]=hashlib.sha256(depout.read_bytes()).hexdigest() if depout.exists() else None
 return (r['returncode']==0 and not r['timed_out'] and r.get('imports_unchanged',False) and
   r.get('import_outputs')==current and r['source_sha256']==hashlib.sha256((root/f).read_bytes()).hexdigest()
   and r['output_sha256']==hashlib.sha256(o.read_bytes()).hexdigest())
done={f for f in order if readyfile(f)}
while True:
 invalid={f for f in done if not deps[f] <= done}
 if not invalid: break
 done-=invalid
pending=set(order)-done;active={};start=time.monotonic();failed=[]
def run(f):
 return subprocess.call([sys.executable,str(root/'tools/lean_one.py'),f,'--log',f'results/v0.28.0/clean_{Path(f).stem}.log'],stdout=subprocess.DEVNULL)
with ThreadPoolExecutor(max_workers=ns.workers) as pool:
 while pending or active:
  if time.monotonic()-start<ns.seconds:
   for f in order:
    if len(active)>=ns.workers:break
    if f in pending and deps[f]<=done:
     pending.remove(f);active[pool.submit(run,f)]=f;print('START',f,flush=True)
  if not active:break
  completed,_=wait(active,return_when=FIRST_COMPLETED)
  for t in completed:
   f=active.pop(t)
   if t.result()==0:done.add(f);print('PASS',f,flush=True)
   else:failed.append(f);print('FAIL',f,(rd/('clean_'+Path(f).stem+'.log')).read_text()[-3000:],flush=True)
  if failed:break
print('CURRENT',len(done),'/',len(order),'REMAINING',len(pending), 'FAILED',failed,flush=True)
sys.exit(1 if failed else 0)
