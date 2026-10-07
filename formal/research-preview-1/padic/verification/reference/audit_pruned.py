#!/usr/bin/env python3
"""Finite exact test contract: dense vs pruned polynomial states and direct Mahler recurrence.
All arithmetic is integer/modular. This is independent implementation evidence,
not a formal Lean/Python refinement or universal proof.
"""
from __future__ import annotations
import sys, json, math, random, time, argparse, platform
from pathlib import Path
from collections import Counter
# Release copy places the unchanged predecessor helper one directory above.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from audit_finite_cartier import Machine,trim,mul,defect,recurrence_coefficients,digit_word
SEED=250920

def valuation(p:int,x:int)->int:
    if not x: raise ValueError('zero has no finite valuation')
    n=0
    while x%p==0: n+=1;x//=p
    return n

def graph_endpoint(p:int,r:int,e:list[int])->int:
    if not any(e):return 1
    h=min(valuation(p,x) for x in e if x)
    K=(r-1)//(h+1)
    def active(q,k):return k*(h+1)+valuation(p,math.comb(q+k-1,k))<r
    B=K//(p-1)+1
    Q=next(q for q in range(1,B+1) if not any(active(j,p*q-j) for j in range(1,q+1)))
    return max(q+k for q in range(1,Q+1) for k in range(K+1) if active(q,k))

class PrunedMachine:
    def __init__(self,full:Machine):
        self.full=full;self.p=full.p;self.r=full.r;self.m=full.m;self.D=full.D
        self.e=full.e;self.M=graph_endpoint(self.p,self.r,self.e)
        self.h=None if not any(self.e) else min(valuation(self.p,x) for x in self.e if x)
    def active(self,ell,k):
        if self.h is None:return k==0
        q=ell//self.p+1
        return k*(self.h+1)+valuation(self.p,math.comb(q+k-1,k))<self.r
    def initial(self):return self.full.initial()[:self.M]
    def embed(self,s):return s+[[0]*(self.D+1) for _ in range(self.full.L-self.M)]
    def step(self,s,d):
        out=[[0]*(self.D+1) for _ in range(self.M)]
        for ell,row in enumerate(s,1):
            for k,(dest,kernel) in enumerate(self.full.kernels[ell-1]):
                if not self.active(ell,k):
                    assert not any(kernel)
                    continue
                assert 1<=dest<=self.M
                sec=trim(mul(row,kernel,self.m)[d::self.p]);assert len(sec)<=self.D+1
                for j,x in enumerate(sec):out[dest-1][j]=(out[dest-1][j]+x)%self.m
        return out
    def output(self,s):return self.full.output(self.embed(s))
    def coefficient(self,n):
        s=self.initial()
        for d in digit_word(self.p,n):s=self.step(s,d)
        return self.output(s)

def audit():
    t=time.monotonic();rng=random.Random(SEED);c=Counter();examples=[]
    def check(b,tag,detail=None):
        c[tag]+=1
        if not b:raise AssertionError((tag,detail))
    cases=[]
    for p in (2,3,5):
      for r in (1,2,3,4):
        masks=[([1,1],[1]),([1],[1,-1]),([1],[1,4]),([1],[1,8]),
               ([1],[1,27]),([1,2,-1],[1,-1,1]),([1,0,1],[1,1])]
        for _ in range(3):
          b0=rng.choice([x for x in (-2,-1,1,2,3) if x%p]);a=[b0]+[rng.randrange(-2,3) for _ in range(2)];b=[b0]+[rng.randrange(-2,3) for _ in range(2)]
          masks.append((a,b))
        for a,b in masks:cases.append((p,r,a,b))
    cases.extend([(2,8,[1],[1,-1]),(3,8,[1],[1,-1])])
    for p,r,a,b in cases:
      full=Machine(p,r,a,b);pr=PrunedMachine(full)
      check(1<=pr.M<=full.L,'layer_count_order',(p,r,b))
      # Independent closure from directly reduced polynomial kernels, no valuation predicate.
      seen={1};todo=[1]
      while todo:
        ell=todo.pop()
        for dest,kernel in full.kernels[ell-1]:
          if any(kernel) and dest not in seen:seen.add(dest);todo.append(dest)
      check(seen==set(range(1,pr.M+1)),'direct_polynomial_graph',(p,r,b))
      for ell in range(1,pr.M+1):
        for k,(dest,kernel) in enumerate(full.kernels[ell-1]):
          act=pr.active(ell,k)
          check(act==bool(any(kernel)),'active_weight_equivalence',(p,r,ell,k))
          check(not act or dest<=pr.M,'active_target_closed')
          if not act:check(all(x==0 for x in kernel),'discarded_is_polynomial_zero')
      oracle=recurrence_coefficients(p,p**r,a,b,48)
      for n,v in enumerate(oracle):
        check(pr.coefficient(n)==v,'pruned_vs_recurrence',(p,r,a,b,n))
        check(pr.coefficient(n)==full.coefficient(n),'pruned_vs_full_output')
      for _ in range(2):
        s=[[rng.randrange(pr.m) for _ in range(pr.D+1)] for _ in range(pr.M)]
        tstate=[[rng.randrange(pr.m) for _ in range(pr.D+1)] for _ in range(pr.M)]
        scalar=rng.randrange(pr.m)
        add=[[ (x+y)%pr.m for x,y in zip(u,v)] for u,v in zip(s,tstate)]
        scale=[[scalar*x%pr.m for x in row] for row in s]
        for d in range(p):
          out=pr.step(s,d)
          check(pr.embed(out)==full.step(pr.embed(s),d),'arbitrary_state_embedding',(p,r,d))
          check(pr.step(add,d)==[[(x+y)%pr.m for x,y in zip(u,v)] for u,v in zip(out,pr.step(tstate,d))],'additivity')
          check(pr.step(scale,d)==[[scalar*x%pr.m for x in row] for row in out],'scalar_linearity')
      check(pr.m**(pr.M*(pr.D+1))<=pr.m**(full.L*(pr.D+1)),'ambient_count_bound')
      if (p,r,a,b) in [(2,3,[1],[1,8]),(2,4,[1],[1,4]),(2,4,[1,1],[1]),(2,8,[1],[1,-1]),(3,8,[1],[1,-1])]:
        examples.append({'p':p,'r':r,'A':a,'B':b,'defect':full.e,'h':pr.h,'old_L':full.L,'pruned_M':pr.M,'D':pr.D,'old_coordinates':full.L*(pr.D+1),'pruned_coordinates':pr.M*(pr.D+1),'old_ambient_count':pr.m**(full.L*(pr.D+1)),'pruned_ambient_count':pr.m**(pr.M*(pr.D+1)),'coefficients_first_16':oracle[:16]})
    return {'status':'PASS','assertions':sum(c.values()),'counts':dict(c),'mask_cases':len(cases),'seed':SEED,'arithmetic':'Python arbitrary-precision integers modulo p^r','python':platform.python_version(),'elapsed_seconds':time.monotonic()-t,'examples':examples,'failures':[], 'non_claims':['Not a universal proof','Python-to-Lean executable refinement unproved','No minimal automaton claim','Coordinate embedding checked here only on finite examples unless separately formalized']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path);a=ap.parse_args();res=audit();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
