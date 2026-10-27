#!/usr/bin/env python3
"""Independent exact rational tests for the Paper III Section 17 analytic identities.

Mathematical validation only: these finite polynomial cases are NOT Lean compilation
and cannot certify universal differentiable Banach-space statements.
"""
import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path

import sympy as sp

SEED = 20261020
rng = random.Random(SEED)
x1,x2,y1,y2,t=sp.symbols('x1 x2 y1 y2 t')
xx=(x1,x2); yy=(y1,y2)

def rnd(low=-3, high=3):
    return sp.Rational(rng.randint(low,high),rng.randint(1,4))

def dot(a,b):
    return sum(a[i]*b[i] for i in range(len(a)))

def dd(f, coords, dirs):
    """Successive directional derivatives, with fixed vector arguments."""
    z=list(f)
    for h in dirs:
        z=[sp.expand(dot(h,[sp.diff(q,c) for c in coords])) for q in z]
    return sp.Matrix(z)

def at(f, coords, v):
    sub={c:v[i] for i,c in enumerate(coords)}
    return sp.Matrix([sp.cancel(q.subs(sub,simultaneous=True)) for q in f])

def matvec(m,v):
    return sp.Matrix(m)*sp.Matrix(v)

def partitions(n):
    """Generate set partitions of range(n) uniquely, canonical block order."""
    blocks=[]
    def rec(i):
        if i==n:
            yield tuple(tuple(b) for b in blocks)
            return
        for j in range(len(blocks)):
            blocks[j].append(i)
            yield from rec(i+1)
            blocks[j].pop()
        blocks.append([i]);yield from rec(i+1);blocks.pop()
    yield from rec(0)

def randpoly(coords,deg=3):
    # Mix all variable interactions and a nonzero quadratic part.
    c,d=coords
    return sp.expand(rnd()*c+ (rnd() or 1)*d+ (rnd() or 1)*c*d + (rnd() or 1)*c**2 + rnd()*d**2 + rnd()*c**2*d + rnd()*d**3)

# Oblique exact complementary projectors: nonorthogonal idempotents.
T=sp.Matrix([[1,1],[0,1]])
U=sp.Matrix([[1,0],[1,1]])
D0=sp.diag(1,0);D1=sp.diag(0,1)
P=(T*D0*T.inv(),T*D1*T.inv())
Q=(U*D0*U.inv(),U*D1*U.inv())
V=(T*D0*T.inv(),T*D1*T.inv())
assert P[0]+P[1] == sp.eye(2) and Q[0]+Q[1] == sp.eye(2)
assert (P[0]*P[1]).is_zero_matrix

checks={};examples={}
def check(key,expr=True):
    assert bool(expr), 'FAIL '+key
    checks[key]=checks.get(key,0)+1

def same(a,b):
    return all(sp.simplify(aa-bb)==0 for aa,bb in zip(a,b))

# General Faà di Bruno with packet decorations, orders 1 through 4.
for trial in range(10):
    G=sp.Matrix([randpoly(xx),randpoly(xx)])
    F=sp.Matrix([randpoly(yy),randpoly(yy)])
    H=sp.Matrix([sp.expand(z.subs({y1:G[0],y2:G[1]},simultaneous=True)) for z in F])
    x0=sp.Matrix([rnd(-2,2),rnd(-2,2)])
    Gx=at(G,xx,x0)
    labels=[trial%2,(trial+1)%2,trial%2, (trial+1)%2]
    raw=[sp.Matrix([rnd(-2,2),rnd(-2,2)]) for _ in range(4)]
    directions=[P[labels[i]]*raw[i] for i in range(4)]
    for n in (1,2,3,4):
        direct=at(dd(H,xx,directions[:n]),xx,x0)
        independent=sp.zeros(2,1);decorated=sp.zeros(2,1)
        term_counter=0
        for partition in partitions(n):
            gblocks=[at(dd(G,xx,[directions[i] for i in b]),xx,x0) for b in partition]
            independent+=at(dd(F,yy,gblocks),yy,Gx)
            for gammatuple in itertools.product(range(2),repeat=len(partition)):
                projected=[Q[j]*gblocks[b] for b,j in enumerate(gammatuple)]
                decorated+=at(dd(F,yy,projected),yy,Gx)
                term_counter+=1
        check('unprojected_partition_chain_rule',same(direct,independent))
        check('all_intermediate_packet_labels',same(direct,decorated))
        for delta in range(2):
            check('literal_output_packet_component',same(V[delta]*direct,V[delta]*decorated))
        expected=sum(int(sp.functions.combinatorial.numbers.stirling(n,k,kind=2))*2**k for k in range(1,n+1))
        check('decorated_term_count',term_counter==expected)
        if trial==0 and n==4:examples={'input_labels':labels,'base_point':[str(v) for v in x0], 'order4_term_count':term_counter}

# Exact Banach Taylor integral remainder via the 1D segment, polynomial directions.
for trial in range(22):
    F=sp.Matrix([randpoly(xx),randpoly(xx)])
    x0=sp.Matrix([rnd(-2,2),rnd(-2,2)])
    h=sp.Matrix([rnd(-2,2),rnd(-2,2)])
    F_on_segment=[sp.expand(q.subs({x1:x0[0]+t*h[0],x2:x0[1]+t*h[1]},simultaneous=True)) for q in F]
    exact=at(F,xx,x0+h)
    for m in (0,1,2,3):
        taylor=sp.zeros(2,1)
        for n in range(m+1):
            taylor+=at(dd(F,xx,[h]*n),xx,x0)/sp.factorial(n)
        remainder=sp.Matrix([
            sp.integrate((1-t)**m*sp.diff(poly,t,m+1),(t,0,1))/sp.factorial(m)
            for poly in F_on_segment
        ])
        check('bochner_integral_polynomial_remainder',same(exact,taylor+remainder))
        for delta in range(2):
            check('projected_integral_remainder',same(V[delta]*exact,V[delta]*(taylor+remainder)))
        if m>=1:
            for n in range(1,m+1):
                reconstructed=sp.zeros(2,1)
                for delta in (0,1):
                    for alphas in itertools.product(range(2),repeat=n):
                        slots=[P[alphas[k]]*h for k in range(n)]
                        reconstructed += V[delta]*at(dd(F,xx,slots),xx,x0)
                check('all_packet_taylor_coefficients',same(at(dd(F,xx,[h]*n),xx,x0), reconstructed))

# Nontrivial logical failure control for the common but wrong one-branch chain rule.
G=sp.Matrix([x1*x2,x1*x1]);F=sp.Matrix([y1+2*y2,3*y1-y2])
x0=sp.Matrix([1,2]);h1=sp.Matrix([1,0]);h2=sp.Matrix([0,1])
H=sp.Matrix([sp.expand(q.subs({y1:G[0],y2:G[1]}, simultaneous=True)) for q in F])
actual=at(dd(H,xx,[h1,h2]),xx,x0)
wrong=at(dd(F,yy,[at(dd(G,xx,[h1]),xx,x0),at(dd(G,xx,[h2]),xx,x0)]),yy,at(G,xx,x0))
check('reject_omission_of_DF_D2G',not same(actual,wrong))

# Check exact norm improvements for concrete nonorthogonal projectors using 1->1 jet.
# Stronger range-bound ||J|| <= ||Q|| ||B||: upper bound tested via sampled exact
# vectors, while universal inequality is justified separately by a proof.
A=sp.Matrix([[2,-1],[1,3]])
for p in P:
    for q in Q:
        for c in range(20):
            v=sp.Matrix([rnd(),rnd()]);z=p*v
            def infinity_norm(vec):return max(abs(k) for k in vec)
            def operator_infty(mat):return max(sum(abs(mat[i,j]) for j in range(mat.cols)) for i in range(mat.rows))
            check('range_jet_strengthened_norm_bound',infinity_norm(q*A*z) <= operator_infty(q)*operator_infty(A)*infinity_norm(z))

receipt={'schema':'komorebi.paper_iii.section17_high_order_checks/1','seed':SEED,
         'status':'PASS','counts':checks,'total_assertions':sum(checks.values()),
         'examples':examples,
         'scope':'Finite-dimensional symbolic polynomial equality and rational norm controls. Universal Banach-space claims require proof; not a Lean kernel replay.',
         'sympy_version':sp.__version__}
out=Path(__file__).parents[1]/'evidence'/'section17_higher_order_tests.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,indent=2))
