#!/usr/bin/env python3
"""Exact finite profile audit. Universal leastness is proved in Lean, not by this sweep."""
from __future__ import annotations
import argparse,itertools,json,math,pathlib,platform,random,sys,time
from collections import Counter
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'reference'))
from audit_finite_cartier import Machine,trim,mul,recurrence_coefficients,digit_word
from audit_pruned import PrunedMachine
from audit_degree_pruned import DegreePrunedMachine
SEED=270920

def cap(poly):
    return len(trim(poly)) if any(poly) else 0

def transfer(p,n,c):
    return 0 if n==0 or c is None else (n-1+c)//p+1

def propagate(p,seed,edges,w):
    out=[max(x,y) for x,y in zip(seed,w)]
    for i,j,c in edges:out[j]=max(out[j],transfer(p,w[i],c))
    return out

def closed(p,seed,edges,w):
    return all(a<=b for a,b in zip(seed,w)) and all(transfer(p,w[i],c)<=w[j] for i,j,c in edges)

class ProfiledMachine:
    def __init__(self,old):
        self.old=old;self.p=old.p;self.r=old.r;self.m=old.m;self.L=old.M;self.U=old.D+1
        self.seed=[cap([x%self.m for x in old.full.b])]+[0]*(self.L-1)
        self.edges=[]
        for i in range(self.L):
            for target,kernel in old.full.kernels[i]:
                if any(kernel):
                    assert 1<=target<=self.L
                    self.edges.append((i,target-1,len(trim(kernel))-1))
        w=[0]*self.L;self.history=[w];self.rounds=0
        for _ in range(self.L*self.U+1):
            out=propagate(self.p,self.seed,self.edges,w)
            assert all(x<=y<=self.U for x,y in zip(w,out))
            if out==w:break
            self.rounds+=1;self.history.append(out);w=out
        else:raise AssertionError('nontermination')
        self.widths=w
    def initial(self):
        rows=[[0]*n for n in self.widths]
        for i,x in enumerate(self.old.full.b):
            if x%self.m:
                assert i<len(rows[0]);rows[0][i]=x%self.m
        return rows
    def embed(self,s):return [row+[0]*(self.U-len(row)) for row in s]
    def step(self,s,d):
        assert [len(x) for x in s]==self.widths
        out=[[0]*n for n in self.widths]
        for i,row in enumerate(s):
            if not any(row):continue
            for target,kernel in self.old.full.kernels[i]:
                if not any(kernel):continue
                product=mul(row,kernel,self.m)
                for n in range(d,len(product),self.p):
                    value=product[n];j=(n-d)//self.p
                    if value:
                        assert j<len(out[target-1]),(i,target,d,j,self.widths)
                        out[target-1][j]=(out[target-1][j]+value)%self.m
        return out
    def output(self,s):
        inv=pow(self.old.full.b[0],-1,self.m)
        return sum((row[0] if row else 0)*pow(inv,i+1,self.m) for i,row in enumerate(s))%self.m
    def coefficient(self,n):
        s=self.initial()
        for d in digit_word(self.p,n):s=self.step(s,d)
        return self.output(s)

def audit():
    start=time.monotonic();rng=random.Random(SEED);counts=Counter();samples=[]
    def ck(ok,kind,detail=None):
        counts[kind]+=1
        if not ok:raise AssertionError((kind,detail))
    # Generic zero-aware systems including no rows, no edges, absent rows, and cycles.
    generic=0
    for L in range(4):
      for D in range(3):
       for p in (1,2,3,4):
        U=D+1
        for trial in range(6):
          seed=[rng.randrange(U+1) for _ in range(L)]
          edges=[(i,j,rng.choice([None]+list(range((p-1)*D+1)))) for i in range(L) for j in range(L)]
          w=[0]*L;hist=[w]
          for _ in range(L*U):w=propagate(p,seed,edges,w);hist.append(w)
          ck(propagate(p,seed,edges,w)==w,'generic_fixed_at_rank_bound')
          for v in itertools.product(range(U+1),repeat=L):
            if closed(p,seed,edges,v):ck(all(x<=y for x,y in zip(w,v)),'exhaustive_generic_leastness')
            ck(all(a<=b for a,b in zip(v,propagate(p,seed,edges,v))),'generic_inflation')
          generic+=1
    masks=[]
    for p in (2,3,5):
      for r in (1,2,3,4,5):
        curated=[([1],[1,-1]),([1],[1,p**2]),([1],[1,p**4]),([1,1],[1]),
                 ([1,0,1],[1,1]),([1],[1,p**(r+1)]),([1+p**r,1],[1,p**2]),
                 ([1,1],[1,1])]
        for _ in range(2):
          c=rng.choice([x for x in (-2,-1,1,2,3) if x%p]);curated.append(([c,rng.randrange(-3,4),rng.randrange(-3,4)],[c,rng.randrange(-3,4),rng.randrange(-3,4)]))
        masks.extend((p,r,a,b) for a,b in curated)
    masks.extend([(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81]),(2,4,[1],[1,4])])
    strict=0
    for p,r,a,b in masks:
      full=Machine(p,r,a,b);old=DegreePrunedMachine(PrunedMachine(full));new=ProfiledMachine(old)
      ck(closed(p,new.seed,new.edges,new.widths),'mask_closed')
      ck(new.rounds<=new.L*new.U,'mask_rank_bound')
      ck(sum(new.widths)<=new.L*new.U,'mask_slot_bound')
      strict+=sum(new.widths)<new.L*new.U
      # A separate asynchronous relaxation has a different iteration order.
      async_w=new.seed.copy()
      for _ in range(new.L*new.U+1):
        previous=async_w.copy()
        for i,j,c in reversed(new.edges):async_w[j]=max(async_w[j],transfer(p,async_w[i],c))
        if previous==async_w:break
      ck(async_w==new.widths,'independent_relaxation_order')
      if new.L<=3 and new.U<=5:
        for candidate in itertools.product(range(new.U+1),repeat=new.L):
          if closed(p,new.seed,new.edges,candidate):
            ck(all(x<=y for x,y in zip(new.widths,candidate)),'exhaustive_mask_leastness')
      ck(new.embed(new.initial())==old.initial(),'initial_embedding')
      oracle=recurrence_coefficients(p,new.m,a,b,32)
      for n,want in enumerate(oracle):
        got=new.coefficient(n)
        ck(got==want,'coefficients_vs_direct_recurrence',(p,r,a,b,n))
        ck(got==old.coefficient(n),'coefficients_vs_block26')
        ck(got==full.coefficient(n),'coefficients_vs_original')
      s=[[rng.randrange(new.m) for _ in range(w)] for w in new.widths]
      t=[[rng.randrange(new.m) for _ in range(w)] for w in new.widths]
      ck(new.output(s)==old.output(new.embed(s)),'arbitrary_output_embedding')
      for d in range(p):
        out=new.step(s,d)
        ck(new.embed(out)==old.step(new.embed(s),d),'arbitrary_transition_embedding')
        plus=[[(a+b)%new.m for a,b in zip(x,y)] for x,y in zip(s,t)]
        ck(new.step(plus,d)==[[(a+b)%new.m for a,b in zip(x,y)] for x,y in zip(out,new.step(t,d))],'linearity')
        before=full.represented(old.embed(new.embed(s)),p*6)
        after=full.represented(old.embed(new.embed(out)),6)
        ck(after==before[d::p],'independent_full_series_semantics')
      if (p,r,a,b) in [(2,4,[1],[1,4]),(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81]),(2,4,[1,1],[1,1])]:
        samples.append({'p':p,'r':r,'A':a,'B':b,'layers':new.L,'D_K':old.D,'capacities':new.widths,
          'degrees':[n-1 if n else None for n in new.widths],'old_slots':new.L*new.U,'new_slots':sum(new.widths),
          'strict_rounds':new.rounds,'round_bound':new.L*new.U,'first16':oracle[:16]})
    # A cycle with no initial support must remain absent; degree zero would not model this.
    w=[0,0]
    edges=[(0,0,2),(1,1,2)]
    seed=[1,0]
    for _ in range(6):w=propagate(2,seed,edges,w)
    ck(w==[2,0],'unseeded_self_loop_stays_absent')
    # Two opposite branch kernels cancel exactly, while degree inequalities do not see that.
    cancellation_profiles=[1,2]
    for d in (0,1):
      u=mul([1],[0,0,1],5);v=mul([1],[0,0,-1],5)
      ck(all((x+y)%5==0 for x,y in zip(u[d::2],v[d::2])),'degree_profile_not_orbit_minimum')
    return {'status':'PASS','assertions':sum(counts.values()),'counts':dict(counts),'seed':SEED,
      'generic_systems':generic,'mask_cases':len(masks),'strict_slot_reductions':strict,'examples':samples,
      'python':platform.python_version(),'seconds':time.monotonic()-start,'failures':[],
      'non_claims':['No finite audit proves universal leastness','Python is not formally refined to Lean',
                    'No optimal automaton or cancellation-sensitive profile claim','No runtime or memory benchmark']}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args()
    result=audit();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
