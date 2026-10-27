"""Finite differential check of the actual Lean accounting function."""
import copy,hashlib,json,os,subprocess,sys,time
from collections import deque
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import run_planner
RD=ROOT/'results/v0.21.0';RD.mkdir(parents=True,exist_ok=True)
def valid(lim,b):
    c,f,n,t,p,h=b
    return c<=lim[0] and n<=lim[1] and f+(t[2] if t else 0)<=c and (not t or t[1]<n) and (not p or t is not None)
def oracle(lim,b,e):
    if not valid(lim,b):return None
    c,f,n,t,p,h=b;k=e[0];r=copy.deepcopy(b)
    if k=='reserve':
        op,fee=e[1:]
        if h or p or t is not None or c+fee>lim[0] or n>=lim[1]:return None
        return [c+fee,f,n+1,[op,n,fee],p,h]
    ticket=e[1]
    if h or ticket!=t:return None
    if k=='renew':
        if p or c+t[2]>lim[0] or n>=lim[1]:return None
        return [c+t[2],f,n+1,[t[0],n,t[2]],p,h]
    if k=='publish':
        if p:return None
        r[4]=True;return r
    if k=='settle':
        if not p:return None
        return [c,f+t[2],n,None,False,h]
    if k=='abandon':
        if p:return None
        return [c,f,n,None,p,True]
    raise AssertionError(k)
requests=[];expected=[];visited_total=0
for credit in [0,1,3,5]:
 for cap in [0,1,3,5]:
    lim=[credit,cap];q=deque([([0,0,0,None,False,False],0)]);seen=set()
    while q:
        b,d=q.popleft();key=json.dumps(b)
        if key in seen:continue
        seen.add(key)
        if d>4:continue
        t=b[3] or [0,0,1]
        tickets=[t,[t[0],t[1]+1,t[2]],[t[0]+1,t[1],t[2]]]
        events=[['reserve',op,f] for op in [0,1] for f in [0,1,2]]
        events += [[k,x] for k in ['renew','publish','settle','abandon'] for x in tickets]
        for e in events:
            r=oracle(lim,b,e);requests.append(['avoc-attempt-v1',lim,b,e]);expected.append(r)
            if r is not None and d<4:q.append((r,d+1))
    visited_total+=len(seen)
for b in [[0,1,0,None,False,False],[0,0,0,None,True,False],[1,0,1,[0,2,1],False,False],[9,0,0,None,False,False]]:
 requests.append(['avoc-attempt-v1',[5,5],b,['reserve',0,1]]);expected.append(None)
path=RD/'attempt_requests.json';path.write_text(json.dumps(requests))
lean,env=run_planner.runtime();cmd=[str(lean),'-j1','-DwarningAsError=true','--run',str(ROOT/'tools/AttemptBatch.lean'),str(path)]
t=time.monotonic();p=subprocess.run(cmd,cwd=ROOT,env=env,capture_output=True,text=True,timeout=90)
(RD/'attempt_batch.stdout').write_text(p.stdout);(RD/'attempt_batch.stderr').write_text(p.stderr)
assert p.returncode==0 and not p.stderr,p.stderr
results=json.loads(p.stdout);assert len(results)==len(expected)
for i,(r,x) in enumerate(zip(results,expected)):
 if x is None:assert r['status']=='error',(i,requests[i],r)
 else:assert r['status']=='ok' and r['ledger']==x,(i,requests[i],r,x)
summary={'passed':True,'requests':len(requests),'unique_states_by_limits':visited_total,
 'successes':sum(x is not None for x in expected),'rejections':sum(x is None for x in expected),
 'seconds':time.monotonic()-t,'command':cmd,'returncode':p.returncode,
 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'request_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
 'lean_source_sha256':hashlib.sha256((ROOT/'AVOC/AttemptAccounting.lean').read_bytes()).hexdigest()}
(RD/'attempt_regression.json').write_text(json.dumps(summary,indent=2));print(summary)
