#!/usr/bin/env python3
"""Exact independent regression against actual executed Lean planner output.
No bounded test is promoted to a universal correctness proof.
"""
from __future__ import annotations
from dataclasses import dataclass,replace
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib, importlib.util, json, sys
ROOT=Path(__file__).resolve().parents[1];RD=ROOT/'results/v0.18.0'
sys.path.insert(0,str(ROOT/'tools'))
from run_planner import run_wire,wire_request,fraction,unique_object

@dataclass(frozen=True)
class State:
    belief:F=F(1,2)
    completed:bool=False
    pending:int=-1
    checked:bool=False
    budget:int=3
    spent:int=0
    generation:int=0
    halted:bool=False

@dataclass(frozen=True)
class Model:
    pf:F;pt:F;rf:int;vf:int;af:int;benefit:F;valid:tuple[bool,...]
    def actions(self,s):
        out=[('stop',-1)]
        if s.halted:return out
        if s.pending>=0 and self.vf<=s.budget:out+=[('verify',-1)]
        if s.pending>=0 and s.checked and self.valid[s.pending] and self.af<=s.budget:out+=[('admit',-1)]
        if not s.completed and self.rf<=s.budget:out += [('register',i) for i in range(len(self.valid))]
        return out
    def prob(self,s,a,d):
        if a[0]!='verify':return F(not d)
        p=(1-s.belief)*self.pf+s.belief*self.pt if s.pending>=0 and self.valid[s.pending] else F(0)
        return p if d else 1-p
    def fee(self,a):return dict(register=self.rf,verify=self.vf,admit=self.af,stop=0)[a[0]]
    def reward(self,s,a):return (self.benefit if a[0]=='admit' and s.checked and s.pending>=0 and self.valid[s.pending] else F(0))-self.fee(a)
    def step(self,s,a,d):
        kind,i=a;fee=self.fee(a)
        z=replace(s,budget=max(0,s.budget-fee),spent=s.spent+fee)
        if kind=='stop':return replace(s,halted=True)
        if kind=='register':return replace(z,pending=i,checked=False,generation=s.generation+1)
        if kind=='admit':return replace(z,completed=True,pending=-1,checked=False)
        p=self.prob(s,a,d);valid=s.pending>=0 and self.valid[s.pending]
        likelihood=(self.pt if d else 1-self.pt) if valid else F(not d)
        post=s.belief*likelihood/p if p else s.belief
        return replace(z,belief=post,checked=d and valid)
    @lru_cache(None)
    def value(self,n,s):
        if n==0:return F(0)
        return max(self.reward(s,a)+sum(self.prob(s,a,d)*self.value(n-1,self.step(s,a,d)) for d in (False,True)) for a in self.actions(s))
    def measured(self,n,s):
        # Independent instrumentation enumerates every edge, including mass zero.
        if n==0:return F(0),None,1
        records=[];work=1
        for a in self.actions(s):
            work+=1;value=self.reward(s,a)
            for d in (False,True):
                work+=1
                v,_,w=self.measured(n-1,self.step(s,a,d));work+=w
                value+=self.prob(s,a,d)*v
            records.append((value,a))
        winner=max(records,key=lambda row:row[0])
        return winner[0],winner[1],work
    def select(self,n,s,credit):
        ka=3+len(self.valid)
        ds=[d for d in range(n+1) if bound(ka,d)<=credit]
        if not ds:return 0,F(0),('stop',-1),0,0
        d=max(ds);v,a,w=self.measured(d,s)
        return d,v,a or ('stop',-1),w,bound(ka,d)
    @lru_cache(None)
    def policy_value(self,n,s,credit):
        if not n:return F(0)
        _,_,a,_,_=self.select(n,s,credit)
        return self.reward(s,a)+sum(self.prob(s,a,d)*self.policy_value(n-1,self.step(s,a,d),credit) for d in (False,True))

def bound(ka,n):
    w=1
    for _ in range(n):w=1+ka*(1+2*(1+w))
    return w

def action(x):return (x['kind'],x.get('candidate',-1))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def check():
    RD.mkdir(exist_ok=True,parents=True)
    jobs=[];cases=[]
    # 3 priors x 4 channels x 3 catalogues x 2 budgets x 5 planning caps.
    for b,(pf,pt),valid,budget,credit in product(
        [F(0),F(1,2),F(1)],[(F(0),F(0)),(F(0),F(1)),(F(1,4),F(3,4)),(F(1),F(1))],
        [(True,),(False,),(False,True)],[2,3],[0,1,21,181,2000]):
        model=Model(pf,pt,1,1,1,F(8),valid);s=State(belief=b,budget=budget)
        n=3
        wire=['avoc-planner-v1',fraction(str(b)),fraction(str(pf)),fraction(str(pt)),1,1,1,[8,1],budget,n,credit,[1,1000],
              '["true"]',['["true"]' if v else '["hyp",["false"]]' for v in valid],[],False]
        jobs.append(wire);cases.append((model,s,n,credit))
    # A finite set of deeper, zero-fee and asymmetric-cost cases.
    for fees,horizon,credit in product([(0,0,0),(0,1,2),(2,1,0)],[1,2,4],[21,2000]):
        rf,vf,af=fees;m=Model(F(1,3),F(2,3),rf,vf,af,F(7,2),(True,));s=State(belief=F(2,3),budget=4)
        jobs.append(['avoc-planner-v1',[2,3],[1,3],[2,3],rf,vf,af,[7,2],4,horizon,credit,[0,1],'["true"]',['["true"]'],[],False]);cases.append((m,s,horizon,credit))
    traces=[]
    for report,credit in product([False,True],[0,181,1461]):
        j=['avoc-planner-v1',[1,2],[1,4],[3,4],1,1,1,[8,1],3,3,credit,[1,1000],'["true"]',['["true"]'],[report],True]
        traces.append(j)
    # Parser/input errors must not be emitted as valid optimization certificates.
    base=jobs[0]
    invalid=[]
    def modified(index,value):
        x=json.loads(json.dumps(base));x[index]=value;invalid.append(x)
    modified(1,[1,0]);modified(1,[2,1]);modified(2,[-1,2]);modified(7,[-1,1]);modified(10,200001)
    modified(9,13);modified(9,0);modified(13,[]);modified(13,['by sorry']);modified(13,['["unknown-rule"]'])
    modified(11,[-1,1]);modified(4,-1);modified(14,[2]);modified(12,'["not-a-formula"]')
    req=jobs+traces+invalid;(RD/'planner_requests.json').write_text(json.dumps(req)+'\n')
    cp,record=run_wire(req,batch=True,timeout=90)
    (RD/'planner_execution.json').write_text(json.dumps(record,indent=2)+'\n')
    (RD/'planner_stdout.jsonl').write_text(cp.stdout);(RD/'planner_stderr.log').write_text(cp.stderr)
    assert cp.returncode==0,cp.stderr
    outputs=[json.loads(line) for line in cp.stdout.splitlines()];assert len(outputs)==len(req)
    gaps=0;zero_support=0
    for out,(m,s,n,credit) in zip(outputs,cases):
        assert out['status']=='ok',out
        r=out['root'];d,v,a,w,res=m.select(n,s,credit)
        assert (r['searched_depth'],F(r['lookahead_value']),action(r['action']),r['work_used'],r['work_reserved'])==(d,v,a,w,res)
        assert v==m.value(d,s)
        assert w<=res<=credit and w+r['unused_credit']==credit
        assert a in m.actions(s)
        q=m.reward(s,a)+sum(m.prob(s,a,o)*m.value(n-1,m.step(s,a,o)) for o in (False,True))
        assert m.value(n,s)-q<=F(r['selected_action_regret_upper'])
        assert F(r['value_lower'])<=m.value(n,s)<=F(r['value_upper'])
        realized_policy=m.policy_value(n,s,credit)
        assert 0<=m.value(n,s)-realized_policy<=F(out['complete_policy_regret_upper'])
        gaps+=int(m.value(n,s)>realized_policy)
        zero_support+=sum(m.prob(s,a,o)==0 for o in (False,True))
    trace_outputs=outputs[len(jobs):len(jobs)+len(traces)]
    for out,j in zip(trace_outputs,traces):
        assert out['status']=='ok',out
        spent=work=0
        for row in out['trace']:
            spent+=row['stage_fee'];work+=row['recommendation']['work_used']
            assert row['after']['research_spent']==spent
            assert row['after']['research_remaining']+spent==3
            if row['recommendation']['action']['kind'] in ('register','verify'):
                assert not row['after']['completed']
        assert work==out['planning_work_total']<=out['total_planning_work_cap']
        assert F(out['declared_planning_charge_total'])==F(work,1000)
    success=trace_outputs[-1]
    assert success['final']['completed'] and success['planning_work_total']==333
    assert [x['recommendation']['action']['kind'] for x in success['trace']]==['register','verify','admit']
    rejected=trace_outputs[2]
    assert rejected['final']['pending'] and not rejected['final']['completed']
    assert F(rejected['final']['posterior_true'])==F(1,4)
    assert all(o['status']=='error' for o in outputs[-len(invalid):])
    wrapper_negatives=0
    for x in [True,0.5,{'num':1}]:
        try:fraction(x)
        except ValueError:wrapper_negatives+=1
        else:raise AssertionError('accepted invalid wrapper rational')
    try:json.loads('{"x":1,"x":2}',object_pairs_hook=unique_object)
    except ValueError:wrapper_negatives+=1
    else:raise AssertionError('duplicate accepted')
    sources=['checks/test_costed_planner.py','tools/run_planner.py','tools/PlannerMain.lean']+[str(p.relative_to(ROOT)) for p in (ROOT/'AVOC').glob('*.lean') if p.name not in ['FullAudit.lean','Audit.lean']]
    result=dict(status='PASS',planner_comparisons=len(jobs),trace_comparisons=len(traces),invalid_wire_rejections=len(invalid),wrapper_rejections=wrapper_negatives,
      positive_policy_loss_cases=gaps,zero_support_selected_branches=zero_support,
      successful_trace_work=333,source_hashes={p:sha(ROOT/p) for p in sources},
      execution_record='results/v0.18.0/planner_execution.json',scope='bounded exact-rational independent model; actual Lean evaluator; no real LLM or filesystem refinement')
    (RD/'planner_regression.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},indent=2))
if __name__=='__main__':check()
