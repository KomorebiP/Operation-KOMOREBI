#!/usr/bin/env python3
"""Exact regression for paid minor probes.
Independent rank oracle enumerates column images, not determinant expressions.
The compiler/kernel proves the universal statements separately from these tests.
"""
from __future__ import annotations
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
sys.path.insert(0, str(ROOT/'checks'))
import probe_affine as app
import test_affine_cache as oracle

RD = ROOT/'results/v0.31.0/probe_tests'


def independent_minor(a, q):
    i,j,k,l=q
    # Enumerating the 25 linear combinations is an orthogonal exact check.
    image={( (x*a[i][k]+y*a[i][l])%5, (x*a[j][k]+y*a[j][l])%5)
           for x in range(5) for y in range(5)}
    return len(image)==25


def expected(p, calls, credit, allowance, plan, out):
    n,m,a,b=oracle.nf(p); old=oracle.tariff(p); pre=oracle.norm_cost(p)+n*m
    assert out['spent']+out['remaining']==credit
    assert oracle.nf(out['selected'])==oracle.nf(p)
    if old==0 or calls==0:
        assert out['status']=='no_deployment_opportunity' and out['spent']==0
        assert out['probe_tests']==0
        return
    if pre>credit:
        assert out['status']=='unfunded_preflight' and out['spent']==0
        return
    base=min(old,oracle.dense(n,m))
    initial=int(any(x for row in a for x in row))
    def facts(lo):
        floor=min(base,oracle.dense(n,m),oracle.factor_cost(n,m,lo))
        minimum=oracle.norm_cost(p)+oracle.reuse_cost(n,m,lo)+oracle.emission(n,m,lo)
        return floor, minimum, minimum<calls*(base-floor)
    _,_,first=facts(initial)
    tested=0; witness=None; lower=initial; available=min(allowance,credit-pre)
    if first:
        for q in plan:
            if available<8: break
            available-=8;tested+=1
            if independent_minor(a,q):
                lower=max(lower,2);witness=q;break
    floor,minimum,last=facts(lower)
    status='skip_initial_bound' if not first else 'skip_probed_bound' if not last else 'search_may_pay'
    assert out['status']==status,(status,out)
    assert out['normal']==dict(input_dim=n,output_dim=m,matrix=a,offset=b)
    assert out['initial_floor']==initial and out['rank_lower_bound']==lower
    assert out['probe_tests']==tested and out['probe_spent']==8*tested
    assert out['spent']==pre+8*tested and out['witness']==witness
    assert out['initial_may_pay']==first and out['final_may_pay']==last
    assert out['menu_cost_floor']==floor and out['remaining_minimum']==minimum
    assert out['opportunity_ceiling']==calls*(base-floor)
    assert out['baseline_proven_two_stage_optimal']==(oracle.factor_cost(n,m,lower)>=base)
    assert out['rank_is_exact'] is False
    if n<=3:
        rank=oracle.exact_rank(n,m,a)
        assert lower<=rank
        # All possible exact factor widths must obey the promised lower costs.
        for width in range(rank, min(m,n)+2):
            assert floor<=min(base,oracle.factor_cost(n,m,width))
            if not last:
                setup=oracle.norm_cost(p)+oracle.reuse_cost(n,m,width)+oracle.emission(n,m,width)
                assert calls*base<=setup+calls*min(base,oracle.factor_cost(n,m,width))


def differential():
    RD.mkdir(parents=True,exist_ok=True)
    requests=[]
    seed=20260914; rng=random.Random(seed)
    for entries in itertools.product(range(5), repeat=4):
        a=[[0]*4 for _ in range(4)]
        a[0][:2]=entries[:2];a[1][:2]=entries[2:]
        p=['map',4,4,a,[0,1,2,3]]
        for allowance in [0,7,8,16]:
            requests.append(['affine-rank-probe-f5-v1',p,1000,100000,allowance,
                             [[0,1,0,1],[0,1,0,1]]])
    for n in range(9):
        for m in range(9):
            p=['map',n,m,[[rng.randrange(5) for _ in range(n)] for _ in range(m)],
               [rng.randrange(5) for _ in range(m)]]
            plan=[[i,j,k,l] for i,j in itertools.combinations(range(m),2)
                  for k,l in itertools.combinations(range(n),2)][:4]
            for calls,credit,allow in [(0,100000,32),(10,3,32),(1000,100000,32)]:
                requests.append(['affine-rank-probe-f5-v1',p,calls,credit,allow,plan])
    for _ in range(100):
        n,m,k=[rng.randrange(1,5) for _ in range(3)]
        def atom(n,m):return ['map',n,m,[[rng.randrange(5) for _ in range(n)] for _ in range(m)],
                             [rng.randrange(5) for _ in range(m)]]
        p=['seq',atom(n,k),atom(k,m)]
        plan=[] if n<2 or m<2 else [[0,1,0,1],[0,0,0,1],[0,1,0,0]]
        requests.append(['affine-rank-probe-f5-v1',p,1000,100000,24,plan])
    # Bounded and duplicated plans are permitted and charged, never silently deduplicated.
    p=['map',4,4,oracle.eye(4),[0]*4]
    for credit in [0,15,16,17,23,24,25,31,32,100000]:
        for allowance in [0,7,8,16]:
            requests.append(['affine-rank-probe-f5-v1',p,1000,credit,allowance,[[0,1,0,1]]])
    for plan in [[[0,0,0,1]],[[0,1,0,0]],[[0,0,0,0]],[],[[0,1,0,1]]*784]:
        requests.append(['affine-rank-probe-f5-v1',p,1000,100000,32,plan])
    start=time.monotonic(); logs=[]; outputs=[]
    for i in range(0,len(requests),180):
        batch=requests[i:i+180]
        out=app.invoke(batch,batch=True,records=logs)
        for req,value in zip(batch,out):expected(*req[1:],value)
        outputs+=out
    malformed=[['bad'], ['affine-rank-probe-f5-v1',p,1,100,8,[[0,4,0,1]]],
      ['affine-rank-probe-f5-v1',p,1,100,8,[[0,1,0]]],
      ['affine-rank-probe-f5-v1',p,1,100,8,[[0,1,0,1]]*785],
      ['affine-rank-probe-f5-v1',p,True,100,8,[]],
      ['affine-rank-probe-f5-v1',p,1,100,-1,[]],
      ['affine-rank-probe-f5-v1',p,1000001,100,8,[]],
      ['affine-rank-probe-f5-v1',['map',1,1,[[5]],[0]],1,100,8,[]],
      ['affine-rank-probe-f5-v1',['seq',['id',1],['id',2]],1,100,8,[]]]
    errors=app.invoke(malformed,batch=True,records=logs)
    assert all(r['status']=='error' for r in errors)
    wrapper_bad=[{'program':p,'rank':2},{'program':p,'probe_plan':[[0,4,0,1]]},
      {'program':p,'probe_credit':1.0},{'program':p,'calls':True},
      {'program':p,'probe_plan':[],'probe_limit':1}]
    for cfg in wrapper_bad:
        try:app.make_request(cfg)
        except ValueError:pass
        else:raise AssertionError('invalid config accepted')
    summary={'passed':True,'seed':seed,'requests':len(requests),'wire_rejections':len(errors),
      'wrapper_rejections':len(wrapper_bad),'seconds':time.monotonic()-start,
      'minor_witnesses':sum(v.get('witness') is not None for v in outputs),
      'probes_executed':sum(v.get('probe_tests',0) for v in outputs),
      'stronger_denials':sum(v.get('status')=='skip_probed_bound' for v in outputs)}
    for name,data in [('differential_summary',summary),('differential_requests',requests),
       ('differential_outputs',outputs),('differential_invocations',logs),('invalid_outputs',errors)]:
        (RD/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


def live():
    RD.mkdir(parents=True,exist_ok=True)
    names=['full_rank','full_rank_no_probe','rank_one','rank_one_no_probe',
           'hidden_witness','missed_witness','unfunded_probe','short_workload']
    outputs={}
    for name in names:
        cfg=app.read_config(ROOT/f'examples/rank_probe/{name}.json')
        if name in ['full_rank','hidden_witness','short_workload']:
            def forbidden(*args):raise AssertionError('forbidden generator call on a denial')
            value=app.run(cfg,generator=forbidden)
        else:value=app.run(cfg)
        outputs[name]=value
        assert value['spent']<=cfg['credit']
        assert oracle.nf(value['selected'])==oracle.nf(cfg['program'])
        for x in cfg['inputs']:
            assert oracle.run(value['selected'],x)==oracle.run(cfg['program'],x)
    assert outputs['full_rank']['spent']==24 and not outputs['full_rank']['generator_executed']
    assert outputs['full_rank_no_probe']['spent']==648
    assert outputs['rank_one']['spent']==248 and outputs['rank_one_no_probe']['spent']==240
    assert outputs['hidden_witness']['probe_tests']==2
    assert outputs['missed_witness']['generator_executed']
    assert outputs['unfunded_probe']['probe_tests']==0
    assert outputs['short_workload']['probe_tests']==0
    for name,value in outputs.items():(RD/('live_'+name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    summary={'passed':True,'live_cases':len(outputs),'results':{k:{f:v.get(f) for f in
      ['status','spent','probe_tests','generator_executed','per_call_selected','net_gain']}
      for k,v in outputs.items()},'physical_speedup_claim':False,
      'protected_store_mutations':0,'oracle':'homogeneous normalization and direct AST evaluation'}
    (RD/'live_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    command=sys.argv[1] if len(sys.argv)>1 else 'differential'
    before={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
      for p in [Path(__file__),ROOT/'tools/probe_affine.py',ROOT/'checks/test_affine_cache.py',ROOT/'tools/factor_affine.py']}
    start=time.time()
    try:
        (differential if command=='differential' else live)()
    finally:
        after={q:hashlib.sha256((ROOT/q).read_bytes()).hexdigest() for q in before}
        RD.mkdir(parents=True,exist_ok=True)
        (RD/f'{command}_source_record.json').write_text(json.dumps({'started_at_unix':start,
          'input_source_before':before,'input_source_after':after,'unchanged':before==after},indent=2)+'\n')
