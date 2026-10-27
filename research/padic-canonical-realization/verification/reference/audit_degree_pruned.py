#!/usr/bin/env python3
"""Bounded exact audit of the degree-pruned machine; not a Lean/Python refinement proof."""
from __future__ import annotations
import argparse, json, math, platform, random, sys, time
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'reference'))
from audit_finite_cartier import Machine, trim, mul, add, power, recurrence_coefficients, digit_word
from audit_pruned import PrunedMachine, valuation
SEED = 260920

class DegreePrunedMachine(PrunedMachine):
    def __init__(self, previous: PrunedMachine):
        super().__init__(previous.full)
        self.previous=previous
        self.K=0 if self.h is None else (self.r-1)//(self.h+1)
        self.C=len(self.full.a)-1+(self.p-1)*(len(self.full.b)-1)+self.K*(len(self.e)-1)
        self.D=max(len(self.full.b)-1,(self.C+self.p-2)//(self.p-1))
    def initial(self):
        rows=[[0]*(self.D+1) for _ in range(self.M)]
        for j,x in enumerate(self.full.b): rows[0][j]=x%self.m
        return rows
    def embed_previous(self,s):
        return [row+[0]*(self.previous.D-self.D) for row in s]
    def embed(self,s):return self.previous.embed(self.embed_previous(s))

def audit():
    started=time.monotonic();rng=random.Random(SEED);counts=Counter();examples=[];cases=[]
    def check(ok,tag,detail=None):
        counts[tag]+=1
        if not ok:raise AssertionError((tag,detail))
    for p in (2,3,5):
      for r in (1,2,3,4,5,6):
        masks=[([1],[1,-1]),([1,1],[1]),([1],[1,p**2]),([1],[1,p**4]),
               ([1,2,-1],[1,p**2,p**2]),([1,0,1],[1,1]),([1+p**r,1],[1,p**2]),
               ([1],[1,p**(r+1)])]
        for _ in range(2):
          b0=rng.choice([x for x in (-2,-1,1,2,3) if x%p])
          masks.append(([b0,rng.randrange(-3,4),rng.randrange(-3,4)],
                        [b0,rng.randrange(-3,4),rng.randrange(-3,4)]))
        cases.extend((p,r,a,b) for a,b in masks)
    cases.extend([(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,8,[1],[1,81]),(5,8,[1],[1,625])])
    strict=0;equal=0
    for p,r,a,b in cases:
      full=Machine(p,r,a,b);old=PrunedMachine(full);new=DegreePrunedMachine(old)
      check(0<=new.K<=r-1,'order_cap',(p,r,b))
      check(len(full.b)-1<=new.D<=old.D,'degree_cap',(p,r,b))
      check(new.M==old.M,'layer_unchanged')
      strict+=new.D<old.D;equal+=new.D==old.D
      check(new.embed_previous(new.initial())==old.initial(),'initial_embedding')
      for ell in range(1,new.M+1):
        q=ell//p+1;t=p*q-(ell+1)
        for k in range(r+3):
          scalar=(-1)**k*math.comb(q+k-1,k)*p**k
          kernel=[scalar*x%new.m for x in mul(mul(full.a,power(full.b,t)),power(full.e,k))]
          kernel=trim(kernel)
          active=new.active(ell,k)
          check(not active or k<=new.K,'active_cap')
          check(k<=new.K or not any(kernel),'above_cap_is_zero')
          check(len(kernel)-1<=(p-1)*new.D,'all_kernel_degrees')
      oracle=recurrence_coefficients(p,new.m,a,b,48)
      for n,want in enumerate(oracle):
        actual=new.coefficient(n)
        check(actual==want,'coefficients_vs_recurrence',(p,r,a,b,n))
        check(actual==old.coefficient(n),'coefficients_vs_block25')
        check(actual==full.coefficient(n),'coefficients_vs_original')
      s=[[rng.randrange(new.m) for _ in range(new.D+1)] for _ in range(new.M)]
      tstate=[[rng.randrange(new.m) for _ in range(new.D+1)] for _ in range(new.M)]
      scalar=rng.randrange(new.m)
      plus=[[(x+y)%new.m for x,y in zip(xr,yr)] for xr,yr in zip(s,tstate)]
      scaled=[[scalar*x%new.m for x in row] for row in s]
      check(new.output(s)==old.output(new.embed_previous(s)),'output_embedding')
      check([row[:new.D+1] for row in new.embed_previous(s)]==s,'embedding_left_inverse')
      for d in range(p):
        out=new.step(s,d)
        check(new.embed_previous(out)==old.step(new.embed_previous(s),d),'arbitrary_transition_embedding')
        check(all(len(trim(row))-1<=new.D for row in out),'outgoing_degree')
        check(new.step(plus,d)==[[(x+y)%new.m for x,y in zip(xr,yr)]
          for xr,yr in zip(out,new.step(tstate,d))],'additivity')
        check(new.step(scaled,d)==[[scalar*x%new.m for x in row] for row in out],'scalar_linearity')
      # Independent full-series realization check on a shorter prefix.
      before=full.represented(new.embed(s),p*8)
      for d in range(p):
        check(full.represented(new.embed(new.step(s,d)),8)==before[d::p],
              'arbitrary_series_semantics')
      ds=[rng.randrange(p) for _ in range(4)];ss=s;tt=new.embed_previous(s)
      for d in ds:ss=new.step(ss,d);tt=old.step(tt,d)
      check(new.embed_previous(ss)==tt,'four_digit_embedding')
      check(new.M*(new.D+1)<=old.M*(old.D+1),'coordinate_count_order')
      if new.h is None or new.h==0:check(new.D==old.D,'zero_or_generic_defect_unchanged_D')
      if r>=2:
        lo=DegreePrunedMachine(PrunedMachine(Machine(p,r-1,a,b)))
        for n in range(12):check(new.coefficient(n)%lo.m==lo.coefficient(n),'precision_reduction')
      if (p,r,a,b) in [(2,4,[1],[1,4]),(2,4,[1],[1,16]),(2,8,[1],[1,16]),(3,6,[1],[1,81]),(2,8,[1],[1,-1])]:
        examples.append({'p':p,'r':r,'A':a,'B':b,'E':full.e,'h':new.h,'K':new.K,
          'old_L':full.L,'pruned_L':new.M,'old_D':old.D,'new_D':new.D,
          'original_slots':full.L*(full.D+1),'block25_slots':new.M*(old.D+1),
          'block26_slots':new.M*(new.D+1),'first16':oracle[:16]})
    # Incorrectly assigning zero cap to a finite nonzero defect loses a real branch.
    f=Machine(2,4,[1],[1,4]);kernel=f.kernels[0][1][1]
    check(any(kernel) and len(kernel)-1>1,'false_zero_cap_counterexample')
    return {'status':'PASS','assertions':sum(counts.values()),'counts':dict(counts),
      'mask_cases':len(cases),'strict_degree_reductions':strict,'unchanged_degree_cases':equal,
      'seed':SEED,'arithmetic':'Python arbitrary-precision integers and exact residues',
      'python_version':platform.python_version(),'runtime_seconds':time.monotonic()-started,
      'examples':examples,'failures':[],
      'non_claims':['Not a universal proof','Not executable Python-to-Lean refinement',
                    'No least layer-specific degree or minimal automaton claim']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    result=audit();args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
