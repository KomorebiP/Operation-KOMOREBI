#!/usr/bin/env python3
"""Exact finite residual-module audit, with independent enumeration and Hankel values.
One asserted scalar/vector/set/matrix equality counts once. No floating point.
The Lean universal theorem is separate from this finite reference computation.
"""
from __future__ import annotations
from pathlib import Path
from itertools import product
from collections import Counter, deque
from math import gcd, prod
import json, random, sys, time, platform
import sympy
from sympy import Matrix, eye, ZZ
from sympy.matrices.normalforms import smith_normal_form
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent/'reference'))
from audit_support import SupportMachine, Machine, PrunedMachine, DegreePrunedMachine, ProfiledMachine, recurrence_coefficients, digit_word
from ideal_engine import IdealMachine
from reachable_engine import reachable_module
from presentation_engine import CyclicPresentation
from observable_engine import ObservablePresentation, exponent
SEED=34092126

def matvec(t,x,m):
    return tuple(sum(a*b for a,b in zip(row,x))%m for row in t)
def run(ts,x,w,m):
    for d in w:x=matvec(ts[d],x,m)
    return x
def out(lam,x,m):return sum(a*b for a,b in zip(lam,x))%m

def orbit(ts,v,m):
    seen={v};q=deque([v])
    while q:
        x=q.popleft()
        for t in ts:
            y=matvec(t,x,m)
            if y not in seen:seen.add(y);q.append(y)
    return seen

def span(gens,m,n):
    ans={tuple(0 for _ in range(n))}
    for g in sorted(gens):
        if g in ans:continue
        ans={tuple((x[i]+a*g[i])%m for i in range(n)) for x in ans for a in range(m)}
    return ans

def words(alpha,k):
    return [w for n in range(k) for w in product(range(alpha),repeat=n)]

def joint_horizon(systems,m,bound):
    """Refine the disjoint union of closed state sets; no matrix normal forms."""
    old=1;ws=[]
    for depth in range(1,bound+2):
        ws+=list(product(range(len(systems[0][0])),repeat=depth-1))
        tables=[{x:tuple(out(lam,run(ts,x,w,m),m) for w in ws) for x in states}
                for ts,lam,states in systems]
        count=len(set().union(*(set(t.values()) for t in tables)))
        if count==old:return depth,ws,tables
        old=count
    raise AssertionError('Observation refinement exceeded declared finite horizon.')

def invertible_change(n,m,rng):
    P=eye(n)
    for _ in range(3*n+1):
        if n>1:
            i,j=rng.sample(range(n),2)
            a=rng.randrange(m)
            P[i,:]=P[i,:]+a*P[j,:]
    inv=P.inv()
    assert all(z.q==1 for z in inv)
    return P.applyfunc(lambda z:int(z)%m),inv.applyfunc(lambda z:int(z)%m)

def main():
    rng=random.Random(SEED);counts=Counter();generic=0;mask_results=[];started=time.monotonic()
    def ck(tag,ok,detail=None):
        counts[tag]+=1
        if not ok:raise AssertionError((tag,detail))
    for p,r in [(2,0),(2,1),(2,2),(3,1),(3,2)]:
      m=p**r
      for n in range(3):
       for alpha in (0,1,2):
        for trial in range(2):
          v=tuple(rng.randrange(m) for _ in range(n))
          ts=tuple(tuple(tuple(rng.randrange(m) for _ in range(n)) for _ in range(n)) for _ in range(alpha))
          lam=tuple(rng.randrange(m) for _ in range(n))
          # Add a driven unobservable coordinate, then hide the decomposition with an invertible change.
          P,Pi=invertible_change(n+1,m,rng)
          nv=tuple(int(z)%m for z in P*Matrix(n+1,1,list(v)+[0]))
          nts=[]
          for t in ts:
              T=Matrix(n+1,n+1,lambda j,i:t[j][i] if j<n and i<n else
                       (rng.randrange(m) if j==n else 0))
              S=P*T*Pi
              nts.append(tuple(tuple(int(S[j,i])%m for i in range(n+1)) for j in range(n+1)))
          nlam=tuple(int(z)%m for z in Matrix(1,n+1,list(lam)+[0])*Pi)
          or1=orbit(ts,v,m);or2=orbit(nts,nv,m)
          r1=span(or1,m,n);r2=span(or2,m,n+1)
          depth,ws,tables=joint_horizon([(ts,lam,r1),(nts,nlam,r2)],m,r*(2*n+1)+1)
          t1,t2=tables;im1=set(t1.values());im2=set(t2.values());generic+=1
          ck('generic_same_initial_behavior',t1[v]==t2[nv])
          ck('generic_residual_image_independent_of_realization',im1==im2)
          ck('generic_image_equals_residual_span',span({t1[x] for x in or1},m,len(ws))==im1)
          ck('generic_second_image_equals_residual_span',span({t2[x] for x in or2},m,len(ws))==im2)
          ck('generic_global_minimum_cardinality',len(im1)<=len(r2)<=m**(n+1))
          ck('generic_finite_comparison_horizon',depth-1<=r*(2*n+1))
          reps1={s:x for x,s in t1.items()};reps2={s:x for x,s in t2.items()}
          for signature in sorted(im1):
              x,y=reps1[signature],reps2[signature]
              ck('generic_output_intertwining',out(lam,x,m)==out(nlam,y,m))
              for d in range(alpha):
                  ck('generic_transition_intertwining',t1[matvec(ts[d],x,m)]==t2[matvec(nts[d],y,m)])
          for _ in range(4):
              a=rng.randrange(m);sx=rng.choice(sorted(im1));sy=rng.choice(sorted(im1))
              x,y=reps1[sx],reps1[sy];nx,ny=reps2[sx],reps2[sy]
              ck('generic_comparison_additive',t1[tuple((a+b)%m for a,b in zip(x,y))]==
                 t2[tuple((a+b)%m for a,b in zip(nx,ny))])
              ck('generic_comparison_scalar',t1[tuple(a*z%m for z in x)]==t2[tuple(a*z%m for z in nx)])
    # Word order is intentionally discriminating.
    ts=(((0,0),(1,0)),((0,1),(0,0)));v=(1,0);lam=(1,0)
    ck('noncommuting_word_order',out(lam,run(ts,v,(0,1),5),5)==1 and out(lam,run(ts,v,(1,0),5),5)==0)
    for u in words(2,4):
      for w in words(2,3):
        ck('prefix_residual_orientation',out(lam,run(ts,v,u+w,5),5)==out(lam,run(ts,run(ts,v,u,5),w,5),5))
    masks=[(p,r,a,b) for p in (2,3) for r in (1,2) for a,b in
           [([1],[1,-1]),([1,1],[1]),([1,1],[1,1])]]
    masks += [(2,4,[1],[1,4]),(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81])]
    for idx,(p,r,a,b) in enumerate(masks):
        full=Machine(p,r,a,b); degree=DegreePrunedMachine(PrunedMachine(full));profile=ProfiledMachine(degree);support=SupportMachine(profile)
        original=IdealMachine(p,r,tuple(support.initial_full),tuple(tuple(tuple(row) for row in t) for t in support.matrices))
        caps=original.least_profile();active=[i for i,c in enumerate(caps) if c>0]
        reduced=IdealMachine(p,r,tuple(original.initial[i] for i in active),tuple(tuple(tuple(t[j][i] for i in active) for j in active) for t in original.matrices))
        reach=reachable_module(reduced);C=CyclicPresentation.construct(reach)
        def actual_output(y):
            x=C.decode(y);z=[0]*original.n
            for i,vv in zip(active,x):z[i]=vv
            return profile.output(support.rows(z))
        lam=[actual_output(tuple(int(i==j) for j in range(len(C.moduli)))) for i in range(len(C.moduli))]
        P=ObservablePresentation.construct(p,r,C.moduli,C.matrices,lam)
        init=C.encode(reduced.initial);qinit=P.encode(init)
        us=words(p,max(1,reach.growth_rounds));ws=words(p,max(1,P.growth_rounds))
        def value(word):return sum(d*p**i for i,d in enumerate(word))
        maxindex=max(value(u)+p**len(u)*value(w) for u in us for w in ws)
        coeff=recurrence_coefficients(p,p**r,a,b,maxindex+1)
        H=Matrix(len(us),len(ws),lambda i,j:coeff[value(us[i])+p**len(us[i])*value(ws[j])])
        for i,u in enumerate(us):
          for j,w in enumerate(ws):
            ck('mask_hankel_entry_direct_recurrence',int(H[i,j])==P.output(P.iterate(u+w,qinit)),(idx,u,w))
        D=smith_normal_form(H,domain=ZZ); sig=[]
        for i in range(min(D.shape)):
            order=p**r//gcd(p**r,abs(int(D[i,i])))
            if order>1:sig.append(exponent(p,order))
        sig=tuple(sorted(sig))
        ck('mask_intrinsic_residual_signature',sig==tuple(sorted(P.signature)),(idx,sig,P.signature))
        ck('mask_residual_cardinality',p**sum(sig)==P.cardinality)
        for n in range(32):
            direct=recurrence_coefficients(p,p**r,a,b,32)[n]
            ck('mask_all_coefficient_reference',P.output(P.iterate(digit_word(p,n),qinit))==direct)
        row={'p':p,'r':r,'A':a,'B':b,'prefixes':len(us),'suffixes':len(ws),'maximum_recurrence_index':maxindex,
             'reachable_exponent':reach.exponent,'minimal_exponent':sum(sig),'residual_signature':sig,
             'cardinality':P.cardinality,'hankel_matrix':[[int(z) for z in row] for row in H.tolist()]}
        mask_results.append(row)
        print('mask',idx+1,'/',len(masks),'Hankel',H.shape,'signature',sig,flush=True)
    # Canonical-encoding agreement alone does not force agreement at [0].
    def trailing(word):return int(bool(word) and word[-1]==0)
    ck('canonical_word_boundary_empty',trailing(())==0)
    for u in words(2,5):ck('canonical_word_boundary_ends_one',trailing(u+(1,))==0)
    ck('noncanonical_word_discriminates',trailing((0,))==1)
    result={'status':'PASS','failures':[],'assertions':sum(counts.values()),'counts':dict(counts),
            'generic_system_pairs':generic,'mask_cases':len(mask_results),'mask_results':mask_results,
            'seed':SEED,'python':platform.python_version(),'sympy':sympy.__version__,'seconds':time.monotonic()-started,
            'non_claims':['Finite audits are not universal proofs.','No Python-to-Lean executable refinement.',
              'Residual signatures use the stated finite prefix/suffix ranges and independently compare with the closure implementation.',
              'No minimum DFA or canonical literal transition matrices.']}
    (ROOT/'results/audit_residual.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='mask_results'},indent=2))
if __name__=='__main__':main()
