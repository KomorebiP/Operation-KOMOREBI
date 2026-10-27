#!/usr/bin/env python3
"""Exact search for atomic weighted-Fano carriers of Fermat fourfold packets.

Arithmetic: Python integers and fractions.Fraction.  A graph is a disjoint
union of directed chains, directed cycles of length >=2, and isolated vertices.
At vertex i the monomial is y_i**n_i*y_next(i), or y_i**n_i at a chain end.
All exponents n_i >=2.  Search includes every such graph on six labeled
vertices and every unit conjugate of a supplied character.

A PASS is a candidate exponent matrix, not a proof of general Hodge.  The
geometric interpretation additionally needs the boundary/graph and uniruled-carrier argument
stated in ../PROOF.md.  Failure is only for this atomic carrier family.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
import platform
import time
from fractions import Fraction as F
from pathlib import Path


def graphs(n: int = 6):
    choices = [(-1,) + tuple(j for j in range(n) if j != i) for i in range(n)]
    for nxt in itertools.product(*choices):
        targets = [j for j in nxt if j != -1]
        if len(targets) != len(set(targets)):
            continue
        prev = [-1]*n
        for i, j in enumerate(nxt):
            if j != -1:
                prev[j] = i
        yield nxt, tuple(prev)


def minimal_exponents(a, m, prev):
    ns=[]
    for i, ai in enumerate(a):
        rhs = 0 if prev[i] == -1 else -a[prev[i]]
        g=math.gcd(ai,m)
        if rhs % g:
            return None
        period=m//g
        residue=((rhs//g)*pow(ai//g,-1,period)) % period
        ni=residue
        if ni < 2:
            ni += ((2-ni+period-1)//period)*period
        assert ni >= 2 and (ni*ai-rhs)%m == 0
        ns.append(ni)
    return tuple(ns)


def weights(ns,nxt):
    """Solve n_i*w_i+w_next=1 exactly by chain and cycle recurrences."""
    n=len(ns)
    w=[None]*n
    for start in range(n):
        if w[start] is not None:
            continue
        path=[]
        pos={}
        cur=start
        while cur != -1 and w[cur] is None and cur not in pos:
            pos[cur]=len(path)
            path.append(cur)
            cur=nxt[cur]
        if cur in pos:
            cyc=path[pos[cur]:]
            # Compose w_cur=A+B*w_cur along the directed cycle.
            A=F(0); B=F(1)
            for i in reversed(cyc):
                A=(1-A)/ns[i]
                B=-B/ns[i]
            w[cur]=A/(1-B)
            tail=path[:pos[cur]]
            # Propagate backwards around the cycle from known w_cur.
            for i in reversed(cyc[1:]):
                w[i]=(1-w[nxt[i]])/ns[i]
            path=tail
        for i in reversed(path):
            following=F(0) if nxt[i] == -1 else w[nxt[i]]
            w[i]=(1-following)/ns[i]
    for i in range(n):
        assert w[i] > 0
        assert ns[i]*w[i]+(0 if nxt[i] == -1 else w[nxt[i]]) == 1
    return tuple(w)


def fracstr(x):
    return str(x.numerator) if x.denominator==1 else f'{x.numerator}/{x.denominator}'


def weighted_model(ws):
    degree=math.lcm(*(w.denominator for w in ws))
    ints=tuple(int(w*degree) for w in ws)
    assert math.gcd(*ints)==1
    ambient_wf=all(math.gcd(*(ints[j] for j in range(6) if j!=i))==1 for i in range(6))
    hypersurface_wf=all(degree%math.gcd(*(ints[j] for j in J))==0 for J in itertools.combinations(range(6),4))
    return {'degree':degree,'weights':ints,'index':sum(ints)-degree,
            'ambient_well_formed':ambient_wf,'hypersurface_well_formed_test':hypersurface_wf}


def search(m, a, all_units=True):
    assert len(a)==6 and all(0<x<m for x in a) and sum(a)%m==0
    units=[t for t in range(1,m) if math.gcd(t,m)==1]
    conjugates=[tuple((t*x)%m for x in a) for t in units]
    balance=all(sum(c)==3*m for c in conjugates)
    if not balance:
        raise ValueError('Input is not a rational middle-Hodge character packet')
    G=list(graphs())
    conjugate_items=list(zip(units,conjugates)) if all_units else [(1,a)]
    best=None; candidates=[]; compatible=0; evaluated=0
    for t,c in conjugate_items:
        for nxt,prev in G:
            ns=minimal_exponents(c,m,prev)
            if ns is None:
                continue
            compatible+=1
            upper=sum((F(1,ni) for ni in ns),F(0))
            # Exact upper bound. Skip only when neither maximum nor Fano list can change.
            if best is not None and upper<=best[0] and upper<=1:
                continue
            ws=weights(ns,nxt)
            s=sum(ws,F(0)); evaluated+=1
            entry={'unit':t,'character':c,'next':nxt,'exponents':ns,
                   'rational_weights':[fracstr(w) for w in ws],
                   'weight_sum':fracstr(s),'model':weighted_model(ws)}
            if best is None or s>best[0]:
                best=(s,entry)
            if s>1:
                candidates.append(entry)
    candidates.sort(key=lambda e:(e['model']['degree'],e['model']['weights'],e['next']))
    return {'modulus':m,'input_character':a,'unit_conjugates':len(units),
            'balanced':balance,'graphs':len(G),'graph_conjugate_pairs':len(G)*len(conjugate_items),
            'compatible_pairs':compatible,'weight_systems_evaluated':evaluated,
            'maximum_weight_sum':best[1] if best else None,
            'fano_candidate_count':len(candidates),
            'well_formed_fano_count':sum(e['model']['ambient_well_formed'] and e['model']['hypersurface_well_formed_test'] for e in candidates),
            'fano_candidates':candidates}


def self_test():
    assert len(list(graphs(2)))==4
    # Pure cubic and a cubic 5-cycle plus a cube.
    assert weights((3,)*6,(-1,)*6)==(F(1,3),)*6
    assert weights((2,2,2,2,2,3),(4,0,1,2,3,-1))==(F(1,3),)*6
    # Unequal 2-cycle and a chain.
    assert weights((2,3),(1,0))==(F(2,5),F(1,5))
    assert weights((2,3),(1,-1))==(F(1,3),F(1,3))
    # Independent rational Gaussian inverse on a deterministic sample.
    import sympy as sp
    for idx,(nxt,prev) in enumerate(graphs()):
        if idx%239:
            continue
        ns=tuple(2+(idx+3*i)%9 for i in range(6))
        A=sp.diag(*ns)
        for i,j in enumerate(nxt):
            if j!=-1:A[i,j]+=1
        expected=tuple(F(x) for x in A.inv()*sp.ones(6,1))
        assert weights(ns,nxt)==expected
    return True


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--modulus',type=int,required=True)
    parser.add_argument('--character',type=int,nargs=6,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    start=time.time()
    self_test()
    result=search(args.modulus,tuple(args.character))
    result['runtime_seconds']=time.time()-start
    result['python']=platform.python_version()
    result['exact_arithmetic']='integers and fractions.Fraction'
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    summary={k:v for k,v in result.items() if k!='fano_candidates'}
    if result['fano_candidates']:
        summary['first_candidate']=result['fano_candidates'][0]
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
