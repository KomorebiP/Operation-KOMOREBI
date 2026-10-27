#!/usr/bin/env python3
"""Exact differential test: direct latent-world cutoff returns vs executed Lean DP.
The independent oracle does not compute posteriors or Bellman recursion for value.
Finite regression, not proof of universal correctness or empirical calibration.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import copy, hashlib, importlib.util, json, sys, time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from run_retry_advisor import run_wire,wire_request
OUT=ROOT/'results/v0.22.0';OUT.mkdir(parents=True,exist_ok=True)

def oracle(c):
    prior=F(c['prior_fast']);qs=[F(c['resolve_if_slow']),F(c['resolve_if_fast'])]
    ws=[1-prior,prior];g=F(c['completion_benefit']);l=copy.deepcopy(c['ledger'])
    fee=l[3][2];prob=sum(w*q for w,q in zip(ws,qs))
    updated=None
    if c.get('observe_operational_fault'):
        if prob==1:return None
        updated=ws[1]*(1-qs[1])/(1-prob);ws=[1-updated,updated]
        prob=sum(w*q for w,q in zip(ws,qs))
    credits=c['attempt_budget']-l[0];slots=c['max_attempts']-l[2];n=c['horizon']
    cap=min(n,slots,credits//fee if fee else n)
    values=[]
    for k in range(cap+1):
        val=sum(w*(g*(1-(1-q)**k)-fee*sum((1-q)**j for j in range(k))) for w,q in zip(ws,qs))
        values.append(val)
    v=max(values)
    action='retry' if cap>0 and prob*g>fee else 'abandon'
    out=copy.deepcopy(l)
    if action=='retry':out[0]+=fee;out[2]+=1;out[3]=[l[3][0],l[2],fee]
    else:out[3]=None;out[5]=True
    return dict(value=v,action=action,prob=prob,net=prob*g-fee,nodes=cap+1,ledger=out,updated=updated,cutoffs=len(values))

start=time.monotonic();cases=[]
for prior,q0,q1,fee,g,h,rem in product([F(0),F(1,2),F(1)],
    [F(0),F(1,4),F(1,2),F(3,4),F(1)],
    [F(0),F(1,4),F(1,2),F(3,4),F(1)], [0,1,2],[0,2,5],[0,1,3,5],[0,3]):
    cases.append(dict(prior_fast=str(prior),resolve_if_slow=str(q0),resolve_if_fast=str(q1),
      completion_benefit=g,attempt_budget=fee+rem,max_attempts=4,
      ledger=[fee,0,1,[0,0,fee],False,False],horizon=h))
base=len(cases)
for c in cases[::11].copy():cases.append(c|{'observe_operational_fault':True})
records=[];cutoffs=0;impossible=0
req_path=OUT/'advisor_requests.jsonl';res_path=OUT/'advisor_results.jsonl'
with req_path.open('w') as rq,res_path.open('w') as rs:
    for offset in range(0,len(cases),600):
        chunk=cases[offset:offset+600];wires=[wire_request(c) for c in chunk]
        outputs,meta=run_wire(wires,batch=True,timeout=45);assert len(outputs)==len(chunk)
        records.append(meta)
        for c,w,r in zip(chunk,wires,outputs):
            rq.write(json.dumps(w,separators=(',',':'))+'\n');rs.write(json.dumps(r,separators=(',',':'))+'\n')
            expected=oracle(c)
            if expected is None:
                assert r['status']=='error' and 'zero declared probability' in r['error'];impossible+=1;continue
            if c.get('observe_operational_fault'):
                assert r['ledger_unchanged'] is True
                assert F(r['posterior_fast'])==expected['updated'];r=r['recommendation']
            assert r['status']=='ok'
            assert F(r['predicted_net_value'])==expected['value'],(c,r,expected)
            assert r['action']==expected['action']
            assert F(r['resolve_probability'])==expected['prob']
            assert F(r['net_one_attempt'])==expected['net']
            assert r['value_evaluation_nodes']==expected['nodes']
            assert r['value_evaluation_nodes']<=r['node_bound']==c['horizon']+1
            assert r['hypothetical_ledger']==expected['ledger']
            assert r['threshold_matches_dynamic_program'] is True
            cutoffs+=expected['cutoffs']
        print('PASS',offset+len(chunk),'/',len(cases),flush=True)
# Invalid inputs are checked by the executed Lean parser/gate, not only Python.
w=wire_request(cases[-2]);
if w[0]=='observe-operational-fault':w=w[1]
invalid=[]
for idx,val in [(1,[2,1]),(2,[-1,1]),(3,[1,0]),(4,[-1,1]),(5,[0,0]),(6,[0,1,0,None,False,False]),(7,33)]:
    ww=copy.deepcopy(w);ww[idx]=val;invalid.append(ww)
invalid += [['unknown-format'],['avoc-retry-decision-v1'],['observe-operational-fault',['broken']]]
outs,meta=run_wire(invalid,batch=True);records.append(meta)
assert all(r['status']=='error' for r in outs),outs
# Published outcomes request reconciliation, not a charged retry.
published=copy.deepcopy(w);published[5]=[20,20];published[6]=[1,0,1,[0,0,1],True,False]
terminal=copy.deepcopy(published);terminal[6]=[1,0,1,None,False,True]
outs,meta=run_wire([published,terminal],batch=True);records.append(meta)
assert [r['status'] for r in outs]==['reconcile_first','terminal']
wrapper_reject=0
for bad in [cases[0]|{'prior_fast':0.5},cases[0]|{'extra':1},cases[0]|{'horizon':True},cases[0]|{'observe_operational_fault':'yes'}]:
    try:wire_request(bad)
    except ValueError:wrapper_reject+=1
    else:raise AssertionError('wrapper accepted bad input')
summary=dict(passed=True,base_comparisons=base,posterior_comparisons=len(cases)-base,
    total_valid_or_zero_support_cases=len(cases),zero_support_rejections=impossible,
    independently_enumerated_cutoff_values=cutoffs,invalid_wire_rejections=len(invalid),
    phase_guard_checks=2,wrapper_rejections=wrapper_reject,seconds=time.monotonic()-start,
    arithmetic='Python Fraction vs executed Lean rational code',
    oracle='Enumerate cutoff returns by integrating (1-(1-q)^k)*gain-fee*sum(1-q)^j directly over latent types',
    range='3 priors x 5 type0 rates x 5 type1 rates x 3 fees x 3 benefits x 4 horizons x 2 remaining credits; slots=3',
    source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    requests_sha256=hashlib.sha256(req_path.read_bytes()).hexdigest(),
    results_sha256=hashlib.sha256(res_path.read_bytes()).hexdigest())
(OUT/'advisor_execution_records.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'advisor_regression.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
