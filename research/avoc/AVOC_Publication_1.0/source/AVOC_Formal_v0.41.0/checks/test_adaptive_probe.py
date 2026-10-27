#!/usr/bin/env python3
"""Exact differential regression for the adaptive paid rank-probe planner.

The Python oracle performs independent finite dynamic programming over determinant
outcome tables. Universal optimality and rank soundness are established in Lean;
this bounded test audits the executable codec and evaluator.
"""
from __future__ import annotations
from fractions import Fraction
from functools import lru_cache
import hashlib,itertools,json,random,sys,time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import plan_rank_probes as app
RD=ROOT/'results/v0.32.0/adaptive_probe_tests'

def q(s):
    s=str(s).replace(' ','')
    if '/' in s:
        a,b=s.split('/',1);return Fraction(int(a),int(b))
    return Fraction(int(s),1)

def det2(a,p):
    i,j,k,l=p
    return (a[i][k]*a[j][l]-a[i][l]*a[j][k])%5!=0

def outcomes(req):
    _,rows,cols,mats,probes,fees,gain,horizon,history=req
    table=tuple(tuple(det2(a,p) for a in mats) for p in probes)
    worlds=tuple(range(len(mats)));remaining=tuple(range(len(probes)));done=False
    for pi,o in history:
        if done or pi not in remaining:raise ValueError('unsupported history')
        support=tuple(w for w in worlds if table[pi][w]==o)
        if not support:raise ValueError('zero probability history')
        remaining=tuple(x for x in remaining if x!=pi)
        if o:done=True;remaining=()
        else:worlds=support
    return table,worlds,remaining,done,tuple(Fraction(x) for x in fees),Fraction(gain),horizon

def solve(req):
    table,worlds0,remaining0,done0,fees,gain,horizon=outcomes(req)
    @lru_cache(None)
    def ev(h,worlds,remaining,done):
        if h==0:return Fraction(0),None,1
        actions=[None] if done else [None,*remaining]
        rows=[]
        for p in actions:
            if p is None:
                reward=Fraction(0);false=(worlds,(),True);true=false;pf=Fraction(1);pt=Fraction(0)
            else:
                sw=tuple(w for w in worlds if table[p][w]);fw=tuple(w for w in worlds if not table[p][w])
                pt=Fraction(len(sw),len(worlds));pf=1-pt;reward=pt*gain-fees[p]
                rem=tuple(x for x in remaining if x!=p)
                false=(fw if fw else worlds,rem,False);true=(worlds,(),True)
            vf,_,wf=ev(h-1,*false);vt,_,wt=ev(h-1,*true)
            score=reward+pf*vf+pt*vt
            work=1+(1+wf)+(1+wt)
            rows.append((score,p,work))
        # Lean's first candidate wins ties.
        best=rows[0]
        for row in rows[1:]:
            if row[0]>best[0]:best=row
        return best[0],best[1],1+sum(x[2] for x in rows)
    return ev(horizon,worlds0,remaining0,done0)

def expected(req,out):
    value,choice,work=solve(req)
    assert out['status']=='optimal_uniform_catalogue_probe_policy',out
    got=out['choice'];gchoice=None if got['kind']=='stop' else got['index']
    assert gchoice==choice,(gchoice,choice,req,out)
    assert q(out['expected_net_value'])==value,(out['expected_net_value'],value)
    assert out['planning_work']==work,(out['planning_work'],work)
    table,worlds,remaining,done,fees,gain,horizon=outcomes(req)
    assert out['state']=={'retained_worlds':len(worlds),'remaining_probes':len(remaining),'done':done}
    probs={r['index']:q(r['success_probability']) for r in out['probe_table']}
    for p in remaining:
        assert probs[p]==Fraction(sum(table[p][w] for w in worlds),len(worlds))
        assert q(next(r['fee'] for r in out['probe_table'] if r['index']==p))==fees[p]

def matrix(rows,cols,rng):return [[rng.randrange(5) for _ in range(cols)] for _ in range(rows)]
def probes(rows,cols,rng,k):
    allp=list(itertools.product(range(rows),range(rows),range(cols),range(cols)))
    allp=[p for p in allp if p[0]!=p[1] and p[2]!=p[3]]
    rng.shuffle(allp);return [list(p) for p in allp[:k]]

def differential():
    RD.mkdir(parents=True,exist_ok=True);rng=random.Random(20260914);requests=[]
    for _ in range(220):
        rows=rng.randrange(2,5);cols=rng.randrange(2,5);nw=rng.randrange(1,7);np=rng.randrange(1,min(7,rows*(rows-1)*cols*(cols-1))+1)
        mats=[matrix(rows,cols,rng) for _ in range(nw)];ps=probes(rows,cols,rng,np)
        fs=[rng.randrange(0,17) for _ in ps];gain=rng.randrange(0,51);h=rng.randrange(0,5)
        req=['adaptive-rank-probe-f5-v1',rows,cols,mats,ps,fs,gain,h,[]]
        requests.append(req)
        # Add one supported failure-history query when possible.
        if h and ps:
            tab=tuple(tuple(det2(a,p) for a in mats) for p in ps)
            fail=[w for w in range(nw) if not tab[0][w]]
            if fail:requests.append(['adaptive-rank-probe-f5-v1',rows,cols,mats,ps,fs,gain,max(0,h-1),[[0,False]]])
    logs=[];outputs=[];start=time.monotonic()
    for i in range(0,len(requests),100):
        batch=requests[i:i+100];out=app.invoke(batch,batch=True,records=logs,timeout=120)
        for req,val in zip(batch,out):expected(req,val)
        outputs+=out
    bad=[['bad'],['adaptive-rank-probe-f5-v1',2,2,[],[],[],1,1,[]],
      ['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,2,0,1]],[1],1,1,[]],
      ['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,1,0,1]],[],1,1,[]],
      ['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,1,0,1]],[1],1,9,[]],
      ['adaptive-rank-probe-f5-v1',2,2,[[[1,0],[0,1]]],[[0,1,0,1]],[1],1,1,[[0,False]]]]
    errors=app.invoke(bad,batch=True,records=logs,timeout=120)
    assert all(x['status']=='error' for x in errors)
    summary={'passed':True,'seed':20260914,'requests':len(requests),'wire_rejections':len(errors),
      'seconds':round(time.monotonic()-start,6),'positive_probe_choices':sum(x['choice']['kind']=='probe' for x in outputs),
      'oracle':'independent determinant tables plus exact Fraction dynamic programming',
      'universal_claim_from_regression':False}
    for name,data in [('differential_summary',summary),('differential_requests',requests),('differential_outputs',outputs),('differential_invocations',logs),('invalid_outputs',errors)]:
        (RD/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

def live():
    RD.mkdir(parents=True,exist_ok=True);records={}
    for name in ['base','after_broad_failure','unequal_fees']:
        req=app.read_request(ROOT/f'examples/adaptive_probe/{name}.json');out=app.invoke(req)
        expected(req,out);records[name]=out;(RD/f'live_{name}.json').write_text(json.dumps(out,indent=2)+'\n')
    assert records['base']['choice']=={'kind':'probe','index':0} and records['base']['expected_net_value']=='26'
    assert records['after_broad_failure']['choice']=={'kind':'probe','index':1} and records['after_broad_failure']['expected_net_value']=='28'
    assert records['unequal_fees']['choice']=={'kind':'probe','index':1} and records['unequal_fees']['expected_net_value']=='9'
    summary={'passed':True,'live_cases':3,'results':{k:{'choice':v['choice'],'value':v['expected_net_value'],'work':v['planning_work']} for k,v in records.items()},'physical_speedup_claim':False,'store_mutations':0}
    (RD/'live_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))

if __name__=='__main__':
    command=sys.argv[1] if len(sys.argv)>1 else 'differential'
    sources=[Path(__file__),ROOT/'tools/plan_rank_probes.py',ROOT/'tools/AdaptiveProbeMain.lean',ROOT/'AVOC/AdaptiveProbeCodec.lean']
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources};start=time.time()
    try:(differential if command=='differential' else live)()
    finally:
        after={q:hashlib.sha256((ROOT/q).read_bytes()).hexdigest() for q in before}
        RD.mkdir(parents=True,exist_ok=True);(RD/f'{command}_source_record.json').write_text(json.dumps({'started_at_unix':start,'input_source_before':before,'input_source_after':after,'unchanged':before==after},indent=2)+'\n')
