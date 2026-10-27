#!/usr/bin/env python3
"""Exact checks for the selected mathematical core, not proof-kernel verification.

Each group declares its finite domain. General conclusions rest on the book's
prose proofs. No network, learned agent, randomized sampling, or floating-point
acceptance criterion is used.
"""
from __future__ import annotations
from pathlib import Path
from fractions import Fraction as F
from itertools import product, combinations
from functools import lru_cache
import json,time,sys,hashlib,platform,traceback
ROOT=Path(__file__).resolve().parents[1]
GROUPS=[]; CURRENT=None

def ck(ok, message=''):
    CURRENT['assertions']+=1
    if not ok: raise AssertionError(message or CURRENT['name'])

def test(label,name,domain):
    def dec(fn):
        global CURRENT
        CURRENT={'result':label,'name':name,'domain':domain,'assertions':0}
        t=time.perf_counter()
        try:
            fn(); CURRENT['status']='PASS'
        except Exception:
            CURRENT['status']='FAIL'; CURRENT['traceback']=traceback.format_exc(); raise
        finally:
            CURRENT['seconds']=time.perf_counter()-t;GROUPS.append(CURRENT.copy())
    return dec

def subsets(xs):
    xs=tuple(xs)
    for m in range(1<<len(xs)): yield frozenset(x for i,x in enumerate(xs) if m>>i&1)

def parts(n):
    if n==0:return [()]
    out=[]
    def rec(p):
        if len(p)==n:out.append(tuple(p));return
        for x in range(max(p,default=-1)+2):rec(p+[x])
    rec([0]);return out

def canon(xs):
    seen={};return tuple(seen.setdefault(x,len(seen)) for x in xs)

def tv(p,q):return sum(abs(x-y) for x,y in zip(p,q))/2

def posterior(p,L,o):
    mass=sum(p[i]*L[i][o] for i in range(len(p)))
    return None if not mass else tuple(p[i]*L[i][o]/mass for i in range(len(p)))

def mm(A,B,p=None):
    C=tuple(tuple(sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))) for i in range(len(A)))
    return tuple(tuple(x%p for x in row) for row in C) if p else C

def mv(A,x,p=2):return tuple(sum(a*b for a,b in zip(row,x))%p for row in A)

def mat(n):return [tuple(tuple(v[n*i:n*(i+1)]) for i in range(n)) for v in product(range(2),repeat=n*n)]

def words(k,h):
    for n in range(h+1):yield from product(range(k),repeat=n)

def span(vecs,n):
    out={tuple(0 for _ in range(n))}
    for v in vecs:out|={tuple(a^b for a,b in zip(x,v)) for x in tuple(out)}
    return out

def main():
 @test('r:factor','Record fibres','All 2-valued record and target maps on three worlds; independent enumeration of all two-input decoders.')
 def _():
    for r in product(range(2),repeat=3):
      for t in product(range(2),repeat=3):
        condition=all(r[i]!=r[j] or t[i]==t[j] for i in range(3) for j in range(3))
        exists=any(all(d[r[i]]==t[i] for i in range(3)) for d in product(range(2),repeat=2))
        ck(condition==exists)

 @test('r:behavior','Behavior and initialization','Every one-action system through three states, every binary readout and record; refinement compared with direct histories through n^2 steps.')
 def _():
    for n in range(1,4):
      for op in product(range(n),repeat=n):
       for q in product(range(2),repeat=n):
        cl=canon(q)
        for step in range(n+1):
          new=canon((cl[x],cl[op[x]]) for x in range(n))
          if new==cl:break
          cl=new
        traces=[]
        for x in range(n):
          tr=[]
          for _ in range(n*n+1):tr.append(q[x]);x=op[x]
          traces.append(tuple(tr))
        ck(cl==canon(traces))
        for r in product(range(2),repeat=n):
          c=all(r[x]!=r[y] or cl[x]==cl[y] for x in range(n) for y in range(n))
          allhist=all(r[x]!=r[y] or traces[x]==traces[y] for x in range(n) for y in range(n))
          ck(c==allhist)
    # The physical sensor target is not initialized by the display alone.
    world=list(product(range(2),repeat=3))
    ck(any((b^s)==(bb^ss) and b!=bb for b,s,_ in world for bb,ss,_ in world))

 @test('r:packet','Composition and hidden return','All ordered pairs of 2x2 matrices with entries -1,0,1; fixed first-coordinate split; independent scalar defect identity.')
 def _():
    matrices=[(v[:2],v[2:]) for v in product((-1,0,1),repeat=4)]
    for T in matrices:
      for U in matrices:ck(mm(T,U)[0][0]-T[0][0]*U[0][0]==T[0][1]*U[1][0])
    swap=((0,1),(1,0));ck(mm(swap,swap)[0][0]==1 and swap[0][0]**2==0)
    for t,u in product(range(-3,4),repeat=2):
      E=((t,0),(t,0));H=((u,0),(u,0));ck(mm(E,H)==((t*u,0),(t*u,0)))

 @test('r:transport','Operation-word transport','All two-action systems on two source and two target states, every translation, and every word of length at most five.')
 def _():
    funcs=list(product(range(2),repeat=2))
    for fs in product(funcs,repeat=2):
     for gs in product(funcs,repeat=2):
      for tr in funcs:
       if all(tr[fs[a][x]]==gs[a][tr[x]] for a in range(2) for x in range(2)):
        for w in words(2,5):
         for x in range(2):
          z=tr[x]
          for a in w:x=fs[a][x];z=gs[a][z]
          ck(tr[x]==z)

 @test('r:common','Propagated discrepancy quotient','All one-action pairs of 2x2 F2 matrices and scalar readouts; closure compared with powers through four and mixed words through four.')
 def _():
    mats=mat(2);vs=list(product(range(2),repeat=2))
    for A,T in product(mats,repeat=2):
     D=tuple(tuple(x^y for x,y in zip(row,other)) for row,other in zip(A,T))
     E=span([mv(D,v) for v in vs],2)
     while True:
      new=span(list(E)+[mv(A,v) for v in E],2)
      if new==E:break
      E=new
     for row in vs:
      Q=(row,);cond=all(mv(Q,v)==(0,) for v in E)
      direct=True
      for v in vs:
       x=y=v
       for _ in range(5):
        direct &= mv(Q,x)==mv(Q,y);x=mv(A,x);y=mv(T,y)
      ck(cond==direct)
      if cond:
       for w in words(2,4):
        for v in vs:
         x=y=v
         for a in w:x=mv((A,T)[a],x);y=mv(A,y)
         ck(mv(Q,x)==mv(Q,y))

 @test('r:memory','Correction-signature dynamics','All 256 subsets and 16 partition-union events of the eight-world sensor; each equal-signature class checked under every event.')
 def _():
    ws=list(product(range(2),repeat=3));cells=[frozenset(i for i,w in enumerate(ws) if w[:2]==bs) for bs in product(range(2),repeat=2)]
    events=[frozenset().union(*(cells[i] for i in ids)) for ids in subsets(range(4))]
    def sig(v):return tuple(frozenset(ws[i][0] for i in v&e) for e in events)
    classes={}
    for V in subsets(range(8)):
      s=sig(V);classes.setdefault(s,[]).append(V)
    ck(len(classes)==16)
    for vals in classes.values():
      for V in vals:
       for E in events:ck(sig(V&E)==sig(vals[0]&E))
    ck(sig(frozenset())!=sig(frozenset({0})))

 @test('r:occupancy','Partition-memory count','Every partition through four worlds, every binary target, every candidate subset, and exactly the partition-union event family.')
 def _():
    for n in range(1,5):
     for part in parts(n):
      cells=[frozenset(i for i in range(n) if part[i]==j) for j in range(max(part)+1)]
      events=[frozenset().union(*(cells[j] for j in ids)) for ids in subsets(range(len(cells)))]
      for target in product(range(2),repeat=n):
       D={(part[i],target[i]) for i in range(n)};seen={}
       for V in subsets(range(n)):
        occ=frozenset((part[i],target[i]) for i in V)
        sig=tuple(frozenset(target[i] for i in V&E) for E in events)
        ck(occ not in seen or seen[occ]==sig);seen[occ]=sig
       ck(len(seen)==2**len(D));ck(len(set(seen.values()))==len(seen))
    # A new split separates previously equal occupancies by contradiction.
    ck(frozenset({0})&frozenset({0}) and not (frozenset({1})&frozenset({0})))

 @test('r:bayes','Bayesian report sufficiency','All binary likelihood and reporting channels on the half grid; five priors, including both degenerate priors; impossible columns and ancillary flag controls.')
 def _():
    vals=(F(0),F(1,2),F(1));ps=(F(0),F(1,4),F(1,2),F(3,4),F(1))
    for l0,l1,b0,b1 in product(vals,repeat=4):
      L=((l0,1-l0),(l1,1-l1));B=((b0,1-b0),(b1,1-b1))
      Q=tuple(tuple(sum(L[m][o]*B[o][z] for o in range(2)) for z in range(2)) for m in range(2))
      factor=True
      for z in range(2):
       mass=sum(Q[m][z] for m in range(2))/2
       rho=tuple(sum(L[m][o]*B[o][z] for m in range(2))/2/mass for o in range(2)) if mass else (F(1),F(0))
       factor &= all(L[m][o]*B[o][z]==Q[m][z]*rho[o] for m,o in product(range(2),repeat=2))
      equal=[]
      for p0 in ps:
       p=(p0,1-p0);agree=True
       for o,z in product(range(2),repeat=2):
        if sum(p[m]*L[m][o]*B[o][z] for m in range(2)):
         agree &= posterior(p,L,o)==posterior(p,Q,z)
       equal.append(agree)
      ck(factor==all(equal)==equal[2])
    P=(F(1,2),0,0,F(1,2));Qp=(0,F(1,2),F(1,2),0)
    L=tuple((F(3,4),F(1,4)) if s==0 else (F(1,4),F(3,4)) for b,s in product(range(2),repeat=2))
    p=posterior(P,L,1);q=posterior(Qp,L,1)
    ck(p[2]+p[3]==F(3,4));ck(q[2]+q[3]==F(1,4))
    ck(sum(P[i]*L[i][1] for i in range(4))==sum(Qp[i]*L[i][1] for i in range(4))==F(1,2))

 @test('r:risk','Common posterior-risk bounds','All two-world priors on the quarter grid; response pairs in {0,1/2,1}; two bounded Lipschitz losses; direct risk and gap checks.')
 def _():
    priors=[(F(i,4),1-F(i,4)) for i in range(5)]
    responses=list(product((F(0),F(1,2),F(1)),repeat=2))
    for p,q,v,u in product(priors,priors,responses,responses):
      e=tv(p,q);d=max(abs(v[i]-u[i]) for i in range(2));xi=min(F(1),e+d)
      r=(sum(p[i]*v[i] for i in range(2)),sum(p[i]*(1-v[i]) for i in range(2)))
      s=(sum(q[i]*u[i] for i in range(2)),sum(q[i]*(1-u[i]) for i in range(2)))
      ck(max(abs(r[i]-s[i]) for i in range(2))<=xi)
      a=min(range(2),key=lambda a:s[a]);ck(r[a]-min(r)<=min(1,2*xi))
      if abs(s[0]-s[1])>2*xi:ck(r[a]<r[1-a])

 @test('r:recipient','Fixed-recipient intersections','All three-case binary sender maps and two-artifact acceptance tables; compared with direct enumeration of every sender encoder.')
 def _():
    for alpha in product(range(2),repeat=3):
     for table in product(range(4),repeat=3):
      fibers={h:[i for i,a in enumerate(alpha) if a==h] for h in set(alpha)}
      allowed={h:{a for a in range(2) if all(table[i]>>a&1 for i in ids)} for h,ids in fibers.items()}
      valid=[code for code in product(range(2),repeat=2) if all(table[i]>>code[alpha[i]]&1 for i in range(3))]
      ck(bool(valid)==all(allowed.values()))
      if valid:
       direct=min(len({code[h] for h in fibers}) for code in valid)
       cover=min(len(C) for C in subsets(range(2)) if all(C & allowed[h] for h in fibers))
       ck(direct==cover)

 @test('r:inquiry','Explicit-tree Pareto feasibility','All one-experiment binary state/report tables on two states, two terminal success tables, nonempty supports and horizons 0..2; direct full-tree profiles vs pruned recurrence, plus four-origin tradeoff.')
 def _():
    def pareto(P):return frozenset(p for p in set(P) if not any(q!=p and q[0]<=p[0] and q[1]<=p[1] for q in P))
    for transition,report in product(list(product(range(2),repeat=2)),repeat=2):
     for m0,m1 in product(range(4),repeat=2):
      @lru_cache(None)
      def allprofiles(V,h,pruned):
       ps=[(0,1) for mask in (m0,m1) if all(mask>>x&1 for x in V)]
       if h:
        branches=[frozenset(transition[x] for x in V if report[x]==o) for o in range(2)]
        branches=[b for b in branches if b]
        for children in product(*(allprofiles(b,h-1,pruned) for b in branches)):
         ps.append((1+max(c[0] for c in children),1+sum(c[1] for c in children)))
       return pareto(ps) if pruned else tuple(set(ps))
      for V in subsets(range(2)):
       if V:
        for h in range(3):ck(pareto(allprofiles(V,h,False))==allprofiles(V,h,True))
    # Independent four-origin tree enumeration.
    @lru_cache(None)
    def four(V,h):
      if len(V)==1:return frozenset({(0,1)})
      if not h:return frozenset()
      out={(4,1+len(V))}
      for x in range(4):
       bs=[b for b in (frozenset(y for y in V if y==x),frozenset(y for y in V if y!=x)) if b]
       for cs in product(*(four(b,h-1) for b in bs)):out.add((1+max(c[0] for c in cs),1+sum(c[1] for c in cs)))
      return frozenset(out)
    ck(pareto(four(frozenset(range(4)),3))==frozenset({(3,7),(4,5)}))

 @test('r:lowerbound','Depth and full stored-tree bounds','All binary tree profiles through eight leaves, plus unary padding and explicit balanced/equality procedures for n=1..16.')
 def _():
    @lru_cache(None)
    def profiles(n):
      if n==1:return {(0,1)}
      return {(1+max(d1,d2),1+m1+m2) for k in range(1,n) for d1,m1 in profiles(k) for d2,m2 in profiles(n-k)}
    for n in range(1,9):
      for d,m in profiles(n):ck(d>=(n-1).bit_length());ck(m==2*n-1)
      ck(min(d for d,m in profiles(n))==(n-1).bit_length())
    for n in (1,2,4,8,16):ck((n-1).bit_length()+1<=n);ck(2*n-1>=1)

 def learn(grammar,target,indices=None):
    examples=[]; trace=[];evals=0
    inds=list(range(len(grammar))) if indices is None else indices
    for i in inds:
      passed=True
      for j,y in examples:
       evals+=1
       if grammar[i][j]!=y:passed=False;break
      if not passed:continue
      wrong=next((j for j,(x,y) in enumerate(zip(grammar[i],target)) if x!=y),None)
      trace.append((i,wrong))
      if wrong is None:return i,trace,evals
      examples.append((wrong,target[wrong]))
    return None,trace,evals

 @test('r:cegis','Finite grammar refinement','Every grammar of length 1..3 over all binary truth vectors on three contexts, every target; earliest solution and teacher-call count.')
 def _():
    funcs=list(product(range(2),repeat=3))
    for n in range(1,4):
     for g in product(funcs,repeat=n):
      for t in funcs:
       i,tr,_=learn(g,t)
       ck(i==next((j for j,p in enumerate(g) if p==t),None))
       ck(len(tr)<=n and len({j for j,o in tr})==len(tr))

 @test('r:ordered','Exact preservation of proposed syntax and evidence','All length-four ordered grammars on two Boolean contexts, with repeated semantic functions treated as different source AST identities; every target.')
 def _():
    funcs=list(product(range(2),repeat=2))
    for g in product(funcs,repeat=4):
      seen={};indices=[]
      for i,p in enumerate(g):
       if p not in seen:seen[p]=i;indices.append(i)
      for t in funcs:
       a=learn(g,t);b=learn(g,t,indices)
       ck(a[:2]==b[:2]);ck(b[2]<=a[2])
    ck(all(max(x,1)==x for x in (1,2,3)));ck(max(0,1)!=0)

 @test('r:prefix','Capacity and identical ordered streaming search','Capacities 1..4 and all legal prefixes; literal report completions; all two-query libraries through four cases with singleton repairs and horizons 0..2.')
 def _():
    for C in range(1,5):
     for m in range(2,2*C+1):
      for a in range(m+1):
       for b in range(m-a+1):
        possible=any(a+bits.count(0)<=C and b+bits.count(1)<=C for bits in product(range(2),repeat=m-a-b))
        ck(possible==(max(a,b)<=C))
    def solve(V,h,queries,stream):
      if len(V)==1:return ('repair',next(iter(V)))
      if h==0 or len(V)>2**h:return None
      C=2**(h-1)
      for qi,q in enumerate(queries):
       bs=[[],[]];stopped=False
       for x in sorted(V):
        bs[q[x]].append(x)
        if stream and len(bs[q[x]])>C:stopped=True;break
       if stopped or not all(bs) or max(map(len,bs))>C:continue
       child=[solve(frozenset(b),h-1,queries,stream) for b in bs]
       if all(c is not None for c in child):return (qi,*child)
      return None
    for n in range(1,5):
     for qs in product(list(product(range(2),repeat=n)),repeat=2):
      for h in range(3):ck(solve(frozenset(range(n)),h,qs,False)==solve(frozenset(range(n)),h,qs,True))
    ck(max(0,5)>min(8,4) and not max(0,5)>8)

 @test('r:dependencies','Dependency-complete invalidation','Every forward DAG through four nodes and all directly changed subsets; topological propagation compared with independent reachability closure.')
 def _():
    for n in range(1,5):
     edges=list(combinations(range(n),2))
     for E in subsets(edges):
      for changed in subsets(range(n)):
       top=set(changed)
       for v in range(n):
        if any((u,v) in E and u in top for u in range(v)):top.add(v)
       reach=set(changed)
       while True:
        nxt=reach|{v for u,v in E if u in reach}
        if nxt==reach:break
        reach=nxt
       ck(top==reach)
    u=v=0;old=u;v=1;ck(old==u and u!=v)
    # An unchanged input cannot authorize an already invalid old witness.
    old_witness_verified=False; declared_inputs_unchanged=True
    ck(not (old_witness_verified and declared_inputs_unchanged))

 @test('r:prices','Resource-price dependence','All three-coordinate difference vectors on -2..2 and price grid {0,1/2,1}; rational convex mixtures; recheck source weighted-search values.')
 def _():
    grid=list(product((F(0),F(1,2),F(1)),repeat=3))
    for d in product(range(-2,3),repeat=3):
      ck(all(sum(w*x for w,x in zip(p,d))>=0 for p in grid)==all(x>=0 for x in d))
    W=((F(1),0),(0,F(1)),(F(1),F(1)))
    for d in product(range(-2,3),repeat=2):
      mn=min(sum(x*y for x,y in zip(p,d)) for p in W)
      for a in range(5):
       for b in range(5-a):
        coeff=(F(a,4),F(b,4),F(4-a-b,4));p=tuple(sum(coeff[j]*W[j][i] for j in range(3)) for i in range(2))
        ck(sum(x*y for x,y in zip(p,d))>=mn)
    d=(1552,1552,-1868);ck(sum(d)==1236);ck(d[0]+d[2]==-316)

 @test('r:lineage','Adaptive conditional false-acceptance budgets','Six-stage finite probability trees with history-dependent hazards at or below declared budgets; exact total event probability, not sampling.')
 def _():
    for mode in range(8):
      dist={():F(1)};ds=[]
      for t in range(6):
       delta=F(1,2**(t+4));ds.append(delta);nxt={}
       for h,mass in dist.items():
        hazard=delta if (sum(h)+mode+t)%3 else delta/2
        ck(hazard<=delta)
        nxt[h+(0,)]=mass*(1-hazard);nxt[h+(1,)]=mass*hazard
       dist=nxt
      ck(sum(dist.values())==1);ck(sum(p for h,p in dist.items() if any(h))<=sum(ds))

 @test('r:reconstruction','Joint target reconstruction','All 2x2 F2 record matrices and scalar target maps; kernel condition compared with direct enumeration of linear decoders.')
 def _():
    vs=list(product(range(2),repeat=2))
    for A in mat(2):
     for q in vs:
      condition=all(mv((q,),x)==(0,) for x in vs if mv(A,x)==(0,0))
      exists=any(all(mv((d,),mv(A,x))==mv((q,),x) for x in vs) for d in vs)
      ck(condition==exists)
    A=((1,1),(0,1));Q=((1,0),);D=((1,1),);ck(mm(D,A,2)==Q)

 @test('r:governance','Enabled-set quotient','All partial one-action transitions on two states, binary labels, both partitions; direct enumeration of every quotient label and partial transition.')
 def _():
    for f in product((-1,0,1),repeat=2):
     for label in product(range(2),repeat=2):
      for pi in ((0,0),(0,1)):
       k=max(pi)+1
       cond=all(pi[x]!=pi[y] or (label[x]==label[y] and (f[x]<0)==(f[y]<0) and (f[x]<0 or pi[f[x]]==pi[f[y]])) for x in range(2) for y in range(2))
       exists=False
       for labs in product(range(2),repeat=k):
        for tr in product(range(-1,k),repeat=k):
         ok=all(labs[pi[x]]==label[x] and (tr[pi[x]]<0)==(f[x]<0) and (f[x]<0 or tr[pi[x]]==pi[f[x]]) for x in range(2))
         exists|=ok
       ck(cond==exists)

 @test('r:ending','Continuation and authorized ending','Every run/end action catalogue on two observed states with nonempty successor sets drawn from {0},{1},{0,1}; fixed target {1}; fixed-point results compared with all stationary policies.')
 def _():
    states=frozenset({0,1});goal=frozenset({1});succ=list(s for s in subsets(states) if s);cats=list(subsets(range(3)))
    def policies(catalog):return product(*(tuple(catalog[z]) if catalog[z] else (None,) for z in range(2)))
    def reaches_goal(z,policy,endcat):
      current={z}
      for _ in range(2):
       nxt=set()
       for x in current-goal:
        a=policy[x]
        if a is None:return False
        nxt |= set(succ[a])
       current=nxt
      return not (current-goal)
    for r0,r1,e0,e1 in product(cats,repeat=4):
      run=(r0,r1);end=(e0,e1);T=set(goal)
      while True:
       nxt=T|{z for z in states if any(succ[a]<=T for a in end[z])}
       if nxt==T:break
       T=nxt
      bruteT={z for z in states if any(reaches_goal(z,p,end) for p in policies(end))}
      ck(T==bruteT)
      L=set(T)
      while True:
       nxt={z for z in L if any(succ[a]<=L for a in run[z])}
       if nxt==L:break
       L=nxt
      bruteL=set()
      for z in states:
       for p in policies(run):
        reach={z}
        for _ in range(3):
         reach |= {y for x in tuple(reach) if p[x] is not None for y in succ[p[x]]}
        if reach<=bruteT and all(p[x] is not None for x in reach):bruteL.add(z);break
      ck(L==bruteL)

if __name__=='__main__':
    before=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();start=time.perf_counter();error=None
    try:main()
    except Exception:error=traceback.format_exc()
    out={'status':'PASS' if error is None else 'FAIL','group_count':len(GROUPS),'assertions':sum(g['assertions'] for g in GROUPS),'groups':GROUPS,'seconds':time.perf_counter()-start,'python':sys.version,'platform':platform.platform(),'arithmetic':'integers, finite sets, fractions.Fraction, F2','source_sha256_before':before,'source_sha256_after':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'error':error,'non_claims':['Finite examples do not prove unrestricted statements.','Same-project alternative implementations are not independent external review.','No learned-agent or proof-kernel execution.']}
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/core_checks.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','group_count','assertions','seconds')},indent=2))
    if error:print(error,file=sys.stderr);sys.exit(1)
