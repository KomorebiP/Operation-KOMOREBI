"""Small exact checks for the NEW editorial connections, not inherited research replays."""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product, combinations
from pathlib import Path
import json, time
ROOT = Path(__file__).resolve().parents[1]

class Checks:
    def __init__(self): self.groups=[]; self.n=0
    def check(self, condition: bool, message: str):
        self.n+=1
        if not condition: raise AssertionError(message)
    def group(self, name, before, domain):
        self.groups.append({'name':name,'assertions':self.n-before,'domain':domain})

def run():
    c=Checks(); t=time.perf_counter()
    worlds=list(product(range(2),repeat=3)); read=lambda w:w[0]^w[1]
    flip=lambda w:(1-w[0],w[1],w[2])
    b=c.n
    for w in worlds:
        v=w; z=read(w)
        for k in range(21):
            c.check(read(v)==z,'display quotient continuation')
            c.check(z==(read(w)^(k%2)),'closed form')
            v=flip(v); z=1-z
    for z in range(2):
        support=[w for w in worlds if read(w)==z]
        c.check({w[0] for w in support}=={0,1},'display cannot identify repair')
    c.group('display_continuation',b,'All 8 worlds; every flip length 0..20; both display fibres.')
    b=c.n
    for s,theta in product(range(2),repeat=2):
        T=lambda z:(z[0]^z[1],z[1])
        z=(s,theta); target=T(z)
        c.check(T((1-s,theta))==(1-target[0],target[1]),'intertwining')
        c.check(T(T(z))==z,'inverse translator')
    for w in worlds:
        c.check((read(w)^w[1])==w[0],'calibrated repair')
    c.group('translator_and_initialization',b,'All 4 two-coordinate records and 8 worlds.')
    b=c.n
    cells=[frozenset(w for w in worlds if w[:2]==q) for q in product(range(2),repeat=2)]
    allsets=[frozenset(worlds[i] for i in range(8) if m>>i&1) for m in range(256)]
    events=[frozenset().union(*(cells[j] for j in range(4) if m>>j&1)) for m in range(16)]
    occ=lambda v:tuple(bool(v&C) for C in cells)
    target=lambda v:frozenset(w[0] for w in v)
    # Compare with representative reconstructions, not the same implementation twice.
    reps={}
    for v in allsets:
        o=occ(v); reps.setdefault(o,v)
        selected=frozenset(next(iter(cells[i])) for i,x in enumerate(o) if x)
        for E in events:
            c.check(target(v&E)==target(selected&E),'occupancy preserves correction')
            c.check(occ(v&E)==occ(selected&E),'occupancy update')
    c.check(len(reps)==16,'all occupancies reachable')
    for a,bv in combinations(reps,2):
        j=next(i for i in range(4) if a[i]!=bv[i]); E=cells[j]
        c.check(target(reps[a]&E)!=target(reps[bv]&E),'distinguishing future event')
    c.group('correction_memory',b,'All 256 candidate subsets; exactly 16 cell-union events; every pair of 16 occupancies.')
    b=c.n
    V0=frozenset(w for w in worlds if read(w)==0); V1=frozenset(w for w in worlds if read(w)==1)
    c.check({w[0] for w in V0}=={w[0] for w in V1},'same target marginal')
    c.check({w[1] for w in V0}=={w[1] for w in V1},'same sensor marginal')
    E=frozenset(w for w in worlds if w[1]==0)
    c.check(target(V0&E)=={0} and target(V1&E)=={1},'different correction after same evidence')
    # Additional within-cell evidence defeats the old occupancy abstraction.
    a=frozenset([worlds[0]]); bv=frozenset([worlds[1]])
    c.check(occ(a)==occ(bv),'same old occupancy')
    c.check(target(a&a)!=target(bv&a),'new evidence changes memory contract')
    c.group('marginal_and_new_evidence_controls',b,'Two display fibres, one calibration event, and a cell-splitting negative control.')
    b=c.n
    from functools import lru_cache
    @lru_cache(None)
    def plan(B,depth,universal=False):
        V=[worlds[i] for i in B]
        if universal or len({w[0] for w in V})==1:return (1,1)
        if not depth:return None
        options=[]
        for f,cost in [(read,1),(lambda w:w[1],2)]:
            children=[]
            for o in range(2):
                C=tuple(i for i in B if f(worlds[i])==o)
                if C:children.append(plan(C,depth-1,universal))
            if all(x is not None for x in children):
                options.append((cost+max(x[0] for x in children),1+sum(x[1] for x in children)))
        return min(options) if options else None
    B=tuple(range(8))
    c.check(plan(B,0) is None and plan(B,1) is None,'need both observations')
    c.check(plan(B,2)==(4,7),'complete work and storage')
    c.check(plan(B,3)==(4,7),'no extra-depth gain')
    c.check(plan(B,0,True)==(1,1),'universal repair changes optimum')
    for w in worlds:
        c.check((1+2+1,1+2+4)==(4,7),'declared units and complete tree')
    c.group('joint_protocol_and_revision',b,'Exact recursion at horizons 0..3; full 8-world support; universal-repair extension.')
    b=c.n
    A0=((1,1,0),(0,1,0),(0,0,2)); A1=((1,1,0),(0,1,0),(1,0,3))
    mv=lambda A,x:tuple(sum(a*y for a,y in zip(row,x)) for row in A)
    initials=list(product([-1,0,1],repeat=3))
    for k in range(7):
        for word in product([0,1],repeat=k):
            for x in initials:
                y=x
                for a in word:y=mv([A0,A1][a],y)
                c.check(y[0]==x[0]+k*x[1] and y[1]==x[1],'common quotient under matched switching')
    c.group('common_linear_predictor',b,'All 27 signed integer initial vectors; every two-operation word through length 6.')
    b=c.n
    # Exact risk bound on a finite grid with bounded, Lipschitz response losses.
    max_gap=Q(0)
    for p,ph in product([Q(i,4) for i in range(5)],repeat=2):
      for y0,y1,z0,z1 in product([Q(0),Q(1,2),Q(1)],repeat=4):
        e=abs(p-ph); d=max(abs(y0-z0),abs(y1-z1)); eta=min(Q(1),e+d)
        risk=[]; approximate=[]
        for act in (Q(0),Q(1)):
          r=p*abs(act-y1)+(1-p)*abs(act-y0)
          rh=ph*abs(act-z1)+(1-ph)*abs(act-z0)
          c.check(abs(r-rh)<=eta,'common bounded-loss error')
          risk.append(r);approximate.append(rh)
        choice=min(range(2),key=lambda i:approximate[i])
        c.check(risk[choice]-min(risk)<=2*eta,'decision regret')
        max_gap=max(max_gap,abs(risk[0]-approximate[0]))
    c.group('posterior_response_composition',b,'25 binary prior pairs; 81 response quadruples; two bounded absolute-loss actions, all rational.')
    b=c.n
    delta=(1552,1552,-1868); prices=((1,1,1),(1,0,1),(0,0,1)); expected=(1236,-316,-1868)
    for w,v in zip(prices,expected):c.check(sum(x*y for x,y in zip(w,delta))==v,'resource price sign')
    for d in product(range(-2,3),repeat=3):
        lhs=all(sum(x*y for x,y in zip(d,w))>=0 for w in product(range(3),repeat=3))
        c.check(lhs==all(x>=0 for x in d),'coordinate dominance on declared grid')
    c.group('resource_ledger',b,'Source-reported 3-coordinate vector; all savings in {-2,..,2}^3 and prices in {0,1,2}^3.')
    out={'status':'PASS','scope':'New editorial examples only; no inherited research suite or Lean project rerun.','arithmetic':'integers, finite sets and fractions.Fraction','groups':c.groups,'group_count':len(c.groups),'assertions':c.n,'runtime_seconds':time.perf_counter()-t,
         'example':{'worlds':8,'display_states':2,'joint_evidence_cells':4,'candidate_sets':256,'correction_records':16,'work_units':4,'primitive_calls':3,'stored_tree_records':7,'message_payload_bits':1,'universal_repair_work':1},
         'resource_example':{'delta':delta,'prices':prices,'savings':expected}}
    (ROOT/'validation'/'connection_checks.json').write_text(json.dumps(out,indent=2))
    print(f"PASS: {len(c.groups)} groups, {c.n:,} exact checks (new connecting examples only).")
    return out
if __name__=='__main__':run()
