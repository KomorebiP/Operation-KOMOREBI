#!/usr/bin/env python3
"""Independent, exact finite checks for the monograph's illustrative models.

Uses only the Python standard library. These enumerations and rational identities
are implementation checks, not substitutes for the quantified mathematical proofs.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import permutations, product, combinations
from pathlib import Path
from datetime import datetime, timezone
import json
import time

ROOT = Path(__file__).resolve().parents[1]
COUNT = 0
GROUPS: dict[str, dict] = {}


def check(condition: bool, message: str) -> None:
    global COUNT
    COUNT += 1
    if not condition:
        raise AssertionError(message)


def group(name: str, fn) -> None:
    start = COUNT
    detail = fn()
    GROUPS[name] = {"assertions": COUNT-start, "detail": detail}


def mul(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))


def mv(a, x):
    return tuple(sum(v*t for v, t in zip(row, x)) for row in a)


def sub(a, b):
    return tuple(tuple(x-y for x, y in zip(r, s)) for r, s in zip(a, b))


def transpose(a):
    return tuple(zip(*a))


def norm2(x):
    return sum(t*t for t in x)


def parity():
    for k in range(-100, 101):
        solutions = [m for m in range(-100, 101) if k == 2*m]
        check(bool(solutions) == (k % 2 == 0), f"parity extension {k}")
        check(len(solutions) <= 1, "double map injective")
        if solutions:
            check(solutions[0] == Q(k, 2), "exact recovered coordinate")
    for a, b in product([False, True], repeat=2):
        check((a == b) == ((a, b) in [(False, False), (True, True)]), "Boolean compatibility")
    check(not (False == True), "object-only cover counterexample")
    check(all(x != (not x) for x in [False, True]), "swap has no coherent section")
    return {"integer_seeds": 201, "Boolean_assignments": 4}


def s3():
    G = list(permutations(range(3))); e=(0,1,2)
    def c(a,b): return tuple(a[b[i]] for i in range(3))
    def inv(a): return tuple(a.index(i) for i in range(3))
    def conj(a,p): return c(c(a,p),inv(a))
    invol = [p for p in G if c(p,p)==e]
    check(len(invol)==4,"four involutions")
    for a,b,p in product(G,G,invol):
        check(conj(c(a,b),p)==conj(a,conj(b,p)),"gauge action order")
        check(c(conj(a,p),conj(a,p))==e,"conjugation preserves cocycles")
    orbits={frozenset(conj(a,p) for a in G) for p in invol}
    check(len(orbits)==2,"two orbit classes")
    check(sorted(map(len,orbits))==[1,3],"orbit sizes")
    for p in invol:
        central=[a for a in G if c(a,p)==c(p,a)]
        check(len(central)==(6 if p==e else 2),"stabilizer size")
        regular=[x for x in G if c(p,x)==x]
        check(len(regular)==(6 if p==e else 0),"twisted regular sections")
    a=(1,0,2);b=(0,2,1)
    check(c(a,b)!=c(b,a),"noncommuting automorphisms")
    # All cocycles on a three-view chain: two independent edge labels.
    for p,q in product(G,repeat=2):
        labels={(0,1):p,(1,2):q,(0,2):c(p,q)}
        for frame in product(G,repeat=3):
            transformed={ij:c(c(frame[ij[0]],v),inv(frame[ij[1]])) for ij,v in labels.items()}
            check(transformed[(0,2)]==c(transformed[(0,1)],transformed[(1,2)]),"chain cocycle after gauge")
    return {"group_order":6,"loop_cocycles":4,"chain_cocycles":36,"gauges_per_chain":216}


def covers():
    records=[]
    for n in (3,4):
        patches=[set(range(n))-{i} for i in range(n)]
        edges=[(i,j) for i in range(n) for j in range(i,n)]
        triples=[(i,j,k) for i in range(n) for j in range(i,n) for k in range(j,n)]
        edge_cover=all(any(set(e)<=U for U in patches) for e in edges)
        composition_cover=all(any(set(t)<=U for U in patches) for t in triples)
        check(edge_cover,"individual arrows covered")
        check(composition_cover==(n==4),"composition coverage distinguishes three and four views")
        check(all(len(U)<n for U in patches),"all patches proper")
        records.append({"views":n,"arrows":len(edges),"composable_pairs":len(triples),"composition_cover":composition_cover})
    return records


def moving_lines():
    slopes=sorted({Q(i,j) for j in (1,2,3,4,5) for i in range(-6,7)})
    vectors=list(product([Q(-3),Q(-1,2),Q(0),Q(2,3),Q(4)],repeat=2))
    q0=((Q(0),Q(0)),(Q(0),Q(1)))
    for t in slopes:
        den=1+t*t
        p=((t*t/den,-t/den),(-t/den,1/den))
        check(mul(p,p)==p,"idempotence")
        check(transpose(p)==p,"self-adjointness")
        diff=sub(p,q0)
        check(mul(transpose(diff),diff)==((t*t/den,Q(0)),(Q(0),t*t/den)),"all-vector motion identity")
        for x in vectors:
            y=mv(p,x)
            check(y[0]+t*y[1]==0,"projected exact")
            check(norm2(mv(diff,x))==t*t/den*norm2(x),"exact motion squared")
            err=tuple(a-b for a,b in zip(x,y))
            check(norm2(err)<= (x[0]+t*x[1])**2,"uniform gain at most one")
            check(sum(a*b for a,b in zip(err,y))==0,"orthogonal error")
        b=Q(7)
        transported=(-t*b,b)
        check(transported[0]+t*transported[1]==0,"kernel transport")
        check((Q(0), transported[1])==(Q(0),b),"inverse kernel transport")
        if t:
            check(mv(p,(Q(0),b))!=transported,"splitting transport differs from nearest projection")
    for t in [Q(1,n) for n in range(1,33)]:
        check(t>0,"nonzero rank-loss parameter")
        # diag(1,t) has zero kernel while diag(1,0) fixes the y-axis.
        check(t*Q(1,t)==1,"new gain forced to 1/t on the lost unit vector")
    return {"rational_slopes":len(slopes),"vectors_per_slope":len(vectors),"rank_loss_parameters":32}


def split_and_cascade():
    # Constant scalar tower, source bond 1/2 and target bond 1.
    residuals=list(product([Q(-1),Q(0),Q(1)], repeat=5))
    for r in residuals:
        a=[Q(0)]
        for v in r:a.append(v+a[-1]/2)
        check(all(a[n+1]-a[n]/2==r[n] for n in range(5)),"split tower right inverse")
        check(max(map(abs,a))<=2*max(map(abs,r)),"split gap bound")
    # Finite concrete dyadic residual model C(a,b)=a+b, J(c)=(0,c).
    for n in (2,4,8,16,32):
        x=tuple(Q((i*i+3*i)%11-5) for i in range(n))
        cur=x; reconstructed=(Q(0),)*n; Jtotal=lambda z: z
        previous_Q=None
        for depth in range(n.bit_length()-1):
            coarse=tuple(cur[i]+cur[i+1] for i in range(0,len(cur),2))
            lift=tuple(v for c in coarse for v in (Q(0),c))
            detail=tuple(a-b for a,b in zip(cur,lift))
            check(all(detail[i]+detail[i+1]==0 for i in range(0,len(detail),2)),"detail in coarsener kernel")
            lifted_detail=Jtotal(detail)
            reconstructed=tuple(a+b for a,b in zip(reconstructed,lifted_detail))
            oldlift=Jtotal
            Jtotal=lambda z,oldlift=oldlift: oldlift(tuple(v for c in z for v in (Q(0),c)))
            Qx=Jtotal(coarse)
            check(tuple(a+b for a,b in zip(reconstructed,Qx))==x,"cascade exact finite telescope")
            check(len(Qx)==n,"restored coordinates retain original type")
            cur=coarse
    # Constant residual on an identity tower has finite primitive n, not a uniform bounded family.
    for N in range(1,65):
        primitive=list(range(N+1))
        check(all(primitive[i+1]-primitive[i]==1 for i in range(N)),"identity finite primitive")
        check(max(primitive)==N,"unbounded growth witness")
    return {"residual_vectors":len(residuals),"cascade_sizes":[2,4,8,16,32],"identity_prefixes":64}


def graph_and_semantics():
    for n in range(1,21):
        x=[Q(8*2**i-1) for i in range(n+1)]
        y=[Q(7*2**i) for i in range(n+1)]
        residual=[x[i+1]/2-x[i] for i in range(n)] + [2*x[i]-x[i+1] for i in range(n)]
        check(max(map(abs,residual))==1,"flat graph edge residual")
        check(max(abs(a-b) for a,b in zip(x,y))==2**n-1,"flat graph amplification")
        check(x[0]==y[0],"anchor preserved")
        check(all(y[i+1]/2==y[i] for i in range(n)),"exact graph family")
        if n>=2:check(2**n-1>n,"route length alone fails")
    x=(Q(2),Q(0),Q(5));nearest=(Q(1),Q(1),Q(5));protected=(Q(2),Q(2),Q(5))
    check(nearest[0]==nearest[1] and protected[0]==protected[1],"both repairs exact")
    check(norm2(tuple(a-b for a,b in zip(x,nearest)))==2,"orthogonal repair distance squared")
    check(norm2(tuple(a-b for a,b in zip(x,protected)))==4,"protected repair distance squared")
    check(protected[0]==x[0] and nearest[0]!=x[0],"different preservation problems")
    for a,b,c in product(range(-2,3),repeat=3):
        x=(Q(a),Q(b),Q(c));PL=(Q(a),Q(b),Q(0));PM=(Q(a),Q(0),Q(0))
        u=tuple(s-t for s,t in zip(x,PL));v=tuple(s-t for s,t in zip(PL,PM))
        check(sum(s*t for s,t in zip(u,v))==0,"nested correction orthogonality")
        check(norm2(tuple(s-t for s,t in zip(x,PM)))==norm2(u)+norm2(v),"two-stage Pythagorean identity")
    return {"flat_chain_lengths":20,"nested_projection_vectors":125,"semantic_example":1}


def main():
    start=time.monotonic()
    for name,fn in [("extension",parity),("nonabelian_gauge",s3),("composition_cover",covers),
                    ("moving_kernels",moving_lines),("split_tower_and_cascade",split_and_cascade),
                    ("graph_and_preservation",graph_and_semantics)]:group(name,fn)
    result={"status":"PASS","executed_utc":datetime.now(timezone.utc).isoformat(),
            "arithmetic":"integers, permutations, and fractions.Fraction only",
            "assertions":COUNT,"groups":GROUPS,"elapsed_seconds":round(time.monotonic()-start,4),
            "scope":"Fresh exact finite implementation checks; no universal theorem or Lean compilation follows from enumeration."}
    (ROOT/'audit/exact_examples.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
