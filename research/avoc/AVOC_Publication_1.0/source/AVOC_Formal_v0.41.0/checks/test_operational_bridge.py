#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,random,subprocess,sys,tempfile,time
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import factor_affine as F
import execute_multi_level as E

SEED=20260914
rng=random.Random(SEED)
MOD=5

def dense(n,m): return m*(2*n+1)

def cost(p):
    tag=p[0]
    if tag=='map': return dense(p[1],p[2])
    if tag=='id': return 0
    if tag=='seq': return cost(p[1])+cost(p[2])
    if tag=='sum': return cost(p[1])+cost(p[2])
    raise ValueError(tag)

def ev(p,x):
    n,m,A,b=F.normal(p)
    assert len(x)==n
    return [(sum(A[i][j]*x[j] for j in range(n))+b[i])%MOD for i in range(m)]

def batch(reqs):
    lean,env=E.runtime('tools/AffineTerminalMain.lean')
    payload=(json.dumps(reqs,separators=(',',':'))+'\n').encode()
    with tempfile.TemporaryDirectory(prefix='avoc_terminal_batch_') as td:
        path=Path(td)/'req.json';path.write_bytes(payload)
        t=time.monotonic()
        cp=subprocess.run([str(lean),'-j1','--run',str(ROOT/'tools/AffineTerminalMain.lean'),'--batch',str(path)],
                          cwd=ROOT,env=env,text=True,capture_output=True,timeout=120)
        sec=time.monotonic()-t
    if cp.returncode:
        raise RuntimeError(cp.stderr+cp.stdout)
    lines=[json.loads(x) for x in cp.stdout.splitlines() if x.strip()]
    assert len(lines)==len(reqs),(len(lines),len(reqs))
    return lines,sec,hashlib.sha256(payload).hexdigest(),hashlib.sha256(cp.stdout.encode()).hexdigest()

def randmat(m,n): return [[rng.randrange(MOD) for _ in range(n)] for _ in range(m)]
def randvec(n): return [rng.randrange(MOD) for _ in range(n)]

def main():
    reqs=[];meta=[]
    # Normalization + cold deployment requests.
    for i in range(32):
        n=rng.randrange(1,5);m=rng.randrange(1,5)
        A=randmat(m,n);b=randvec(m);p=['map',n,m,A,b]
        calls=rng.randrange(0,101);meter=F.Meter(10**8);cand=F.certificate(n,m,A,b,meter)
        ins=[randvec(n) for _ in range(4)]
        reqs.append(['affine-terminal-normalize-f5-v1',p]);meta.append(('norm',p,None,calls,ins,None))
        reqs.append(['affine-terminal-cold-f5-v1',p,cand,calls,meter.spent,10**8,ins]);meta.append(('cold',p,cand,calls,ins,meter.spent))
    # Warm retargeting under equal linear maps and changed offsets.
    for i in range(20):
        n=rng.randrange(1,5);m=rng.randrange(1,5);A=randmat(m,n)
        oldb=randvec(m);newb=randvec(m)
        meter=F.Meter(10**8);cand=F.certificate(n,m,A,oldb,meter)
        record=['avoc-affine-cache-f5-dense-v1',n,m,A,oldb,cand]
        p=['map',n,m,A,newb];calls=rng.randrange(1,101);ins=[randvec(n) for _ in range(4)]
        reqs.append(['affine-terminal-warm-f5-v1',p,record,calls,0,10**8,ins]);meta.append(('warm',p,cand,calls,ins,None))
    # Exact probe reports.
    for i in range(30):
        n=rng.randrange(2,5);m=rng.randrange(2,5);A=randmat(m,n);b=randvec(m);p=['map',n,m,A,b]
        if i%2:
            r1,r2=sorted(rng.sample(range(m),2));c1,c2=sorted(rng.sample(range(n),2))
            probe=['minor2',r1,r2,c1,c2]
        else:
            probe=['entry',rng.randrange(m),rng.randrange(n)]
        reqs.append(['affine-terminal-probe-f5-v1',p,probe]);meta.append(('probe',p,probe,0,[],None))
    # Six malformed/unsupported requests.
    invalid=[['wrong-tag'],
             ['affine-terminal-normalize-f5-v1',['map',2,2,[[1]],[0,0]]],
             ['affine-terminal-probe-f5-v1',['id',1],['entry',4,0]],
             ['affine-terminal-cold-f5-v1',['id',1],[9,[],[],[],[],[],[]],1,0,100,[]],
             ['affine-terminal-warm-f5-v1',['id',1],['wrong'],1,0,100,[]],
             ['affine-terminal-normalize-f5-v1',['unknown']]]
    for q in invalid:reqs.append(q);meta.append(('invalid',q,None,0,[],None))
    outs,sec,reqhash,outhash=batch(reqs)
    counts={k:0 for k in ['norm','cold','warm','probe','invalid']};vectors=0
    for info,out in zip(meta,outs):
        kind,p,extra,calls,ins,generation=info;counts[kind]+=1
        if kind=='invalid':
            assert out['status']=='error',out
            continue
        n,m,A,b=F.normal(p)
        if kind=='norm':
            assert out['status']=='certified_affine_normal_form'
            assert out['normal']['matrix']==A and out['normal']['offset']==b
            assert out['per_call_original']==cost(p)
        elif kind in ('cold','warm'):
            expected='certified_cold_deployment' if kind=='cold' else 'certified_warm_deployment'
            assert out['status']==expected,out
            d=out['deployment'];selected=d['selected']
            nn,mm,AA,bb=F.normal(selected)
            assert (nn,mm,AA,bb)==(n,m,A,b)
            assert d['per_call_selected']<=d['per_call_original']==cost(p)
            assert d['outputs']==[ev(p,x) for x in ins]
            vectors+=len(ins)
            payoff=Fraction(d['modeled_net_payoff'])
            assert payoff==calls*(d['per_call_original']-d['per_call_selected'])-d['setup_charge']
            assert d['kind']==kind
        elif kind=='probe':
            assert out['status']=='exact_affine_probe_report'
            q=extra
            if q[0]=='entry': expected=A[q[1]][q[2]]%MOD!=0
            else:
                _,r1,r2,c1,c2=q
                expected=(A[r1][c1]*A[r2][c2]-A[r1][c2]*A[r2][c1])%MOD!=0
            assert out['report'] is expected
            assert out['certified_level']==(1 if q[0]=='entry' else 2)
    summary={'seed':SEED,'requests':len(reqs),'counts':counts,'input_vector_comparisons':vectors,
             'seconds':round(sec,6),'request_sha256':reqhash,'stdout_sha256':outhash,'status':'pass'}
    out=ROOT/'results/v0.34.0/operational/bridge_regression.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
