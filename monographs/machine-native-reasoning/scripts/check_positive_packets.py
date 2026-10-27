#!/usr/bin/env python3
"""Exact finite regression for Core 2.5. Standard-library rational arithmetic only.

The general Lean proofs are separate. This checker exhausts the stated matrix
families and tests normalized packets under specified positive masses and exact
coordinate changes. No random sampling, tolerance, training or runtime claim.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
from typing import Sequence

Vector = tuple[F, ...]
Matrix = tuple[Vector, ...]


def eye(n: int) -> Matrix:
    return tuple(tuple(F(int(r == c)) for c in range(n)) for r in range(n))


def matrix(flat: Sequence[int], n: int, denominator: int = 2) -> Matrix:
    if len(flat) != n * n or denominator <= 0:
        raise ValueError('invalid matrix shape or denominator')
    return tuple(tuple(F(flat[n*r+c], denominator) for c in range(n)) for r in range(n))


def add(a: Matrix, b: Matrix) -> Matrix:
    if len(a) != len(b) or any(len(x) != len(y) for x,y in zip(a,b)):
        raise ValueError('matrix dimension mismatch')
    return tuple(tuple(x+y for x,y in zip(ar,br)) for ar,br in zip(a,b))


def scale(a: Matrix, c: F) -> Matrix:
    return tuple(tuple(c*x for x in row) for row in a)


def mul(a: Matrix, b: Matrix) -> Matrix:
    n=len(a)
    if len(b) != n or any(len(r) != n for r in a+b):
        raise ValueError('only compatible square matrices are admitted')
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(n)), F())
                       for j in range(n)) for i in range(n))


def apply(a: Matrix, v: Vector) -> Vector:
    if any(len(r) != len(v) for r in a):
        raise ValueError('vector dimension mismatch')
    return tuple(dot(r,v) for r in a)


def dot(a: Vector, b: Vector) -> F:
    if len(a) != len(b):
        raise ValueError('mass dimension mismatch')
    return sum((x*y for x,y in zip(a,b)), F())


def nonnegative(a: Matrix) -> bool:
    return all(x >= 0 for row in a for x in row)


def sum_vectors(vectors: Sequence[Vector], n: int) -> Vector:
    if any(len(v) != n for v in vectors):
        raise ValueError('vector-sum dimension mismatch')
    return tuple(sum((v[j] for v in vectors), F()) for j in range(n))


def mixture(family: tuple[Matrix,...], mass: Vector, v: Vector,
            inverse_chart: Matrix) -> tuple[tuple[F,...],dict[int,Vector]]:
    assert dot(mass,v) == 1
    assert all(x >= 0 for x in apply(inverse_chart,v))
    pieces=tuple(apply(p,v) for p in family)
    weights=tuple(dot(mass,x) for x in pieces)
    assert all(w >= 0 for w in weights)
    assert sum(weights,F()) == 1
    states={}
    for i,(w,x) in enumerate(zip(weights,pieces)):
        assert all(t >= 0 for t in apply(inverse_chart,x))
        if not w:
            assert all(t == 0 for t in x)
        else:
            assert w > 0
            states[i]=tuple(t/w for t in x)
            assert dot(mass,states[i]) == 1
            assert all(t >= 0 for t in apply(inverse_chart,states[i]))
    reconstructed=sum_vectors([tuple(weights[i]*t for t in x) for i,x in states.items()],len(v))
    assert reconstructed == v
    assert sum((weights[i] for i in states),F()) == 1
    return weights,states


def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    counts=Counter()
    domain=[]
    positive_families=[]
    # One family member is determined by completeness. The integer-grid
    # representation is used only to enumerate candidates, not to round data.
    for n,m,grid in [(2,2,tuple(range(-2,5))),(2,3,(0,1,2)),(3,2,(0,1,2))]:
        local=Counter()
        for values in product(grid,repeat=(m-1)*n*n):
            first=[tuple(values[k*n*n:(k+1)*n*n]) for k in range(m-1)]
            last=tuple(2*int(r==c)-sum(p[r*n+c] for p in first)
                       for r in range(n) for c in range(n))
            raw=first+[last]
            local['families']+=1
            if not all(x >= 0 for p in raw for x in p):
                continue
            local['positive_complete']+=1
            # Exhaustively check the claimed off-diagonal implication.
            assert all(p[r*n+c] == 0 for p in raw for r in range(n) for c in range(n) if r!=c)
            fam=tuple(matrix(p,n) for p in raw)
            idempotent=all(mul(p,p)==p for p in fam)
            is_selector=all(x in (0,2) for p in raw for x in p)
            assert idempotent == is_selector
            if idempotent:
                local['selector_families']+=1
                owner=[]
                for r in range(n):
                    selected=[i for i,p in enumerate(fam) if p[r][r]==1]
                    assert len(selected)==1
                    owner.append(selected[0])
                zero=scale(eye(n),F())
                for i,p in enumerate(fam):
                    expected=tuple(tuple(F(int(r==c and owner[r]==i)) for c in range(n)) for r in range(n))
                    assert p==expected
                    for j,q in enumerate(fam):
                        assert mul(p,q)==(p if i==j else zero)
            positive_families.append((n,fam))
        domain.append({'dimension':n,'packets':m,'free_coefficient_numerators':list(grid),
                       'denominator':2,**dict(local)})
        counts.update(local)
    for n,fam in positive_families:
        for m in product((1,2),repeat=n):
            mass=tuple(map(F,m))
            for raw in product(range(3),repeat=n):
                if not any(raw):
                    continue
                u=tuple(map(F,raw)); total=dot(mass,u)
                v=tuple(x/total for x in u)
                weights,states=mixture(fam,mass,v,eye(n))
                counts['coordinate_mixture_inputs']+=1
                counts['zero_weight_packets']+=sum(w==0 for w in weights)
                if n!=2:
                    continue
                for t in (-2,-1,1,2):
                    chart=((F(1),F(t)),(F(0),F(1)))
                    inverse=((F(1),F(-t)),(F(0),F(1)))
                    assert mul(chart,inverse)==eye(2)==mul(inverse,chart)
                    moved=tuple(mul(mul(chart,p),inverse) for p in fam)
                    moved_mass=tuple(sum((mass[r]*inverse[r][c] for r in range(2)),F()) for c in range(2))
                    moved_v=apply(chart,v)
                    new_weights,new_states=mixture(moved,moved_mass,moved_v,inverse)
                    assert new_weights==weights
                    assert new_states=={i:apply(chart,x) for i,x in states.items()}
                    counts['transported_mixture_inputs']+=1
                    counts['signed_valid_transported_states']+=sum(any(c<0 for c in x) for x in new_states.values())
    E=eye(2); Z=scale(E,F())
    average=((F(1,2),F(1,2)),(F(1,2),F(1,2)))
    detail=add(E,scale(average,F(-1)))
    assert add(average,detail)==E
    assert mul(average,average)==average and mul(detail,detail)==detail
    assert mul(average,detail)==Z and mul(detail,average)==Z
    v=(F(3,4),F(1,4)); d=apply(detail,v)
    assert d==(F(1,4),F(-1,4)) and sum(d,F())==0 and d!=(F(),F())
    counts['boundary_checks']+=1
    # Strict positivity cannot be replaced by nonnegative mass.
    assert dot((F(1),F(0)),(F(0),F(1)))==0
    counts['boundary_checks']+=1
    half=scale(E,F(1,2)); assert add(half,half)==E and mul(half,half)!=half
    counts['boundary_checks']+=1
    assert sum(apply(half,(F(1),F(0))),F())==F(1,2)
    counts['boundary_checks']+=1
    assert sum(apply(scale(E,F(-1)),(F(1),F(0))),F())==-1
    counts['boundary_checks']+=1
    assert mul(E,E)!=Z  # Idempotence and positivity without completeness allow overlap.
    counts['boundary_checks']+=1
    assert dot((F(1),F(1)),(F(2),F(0)))==2  # Non-unit input does not have total weight one.
    counts['boundary_checks']+=1
    assert tuple()==eye(0) and sum_vectors([],0)==tuple()
    counts['boundary_checks']+=1
    report={'schema':'komorebi.core25.exact-finite.v1','status':'PASS','arithmetic':'integer and exact Fraction',
            'matrix_domains':domain,'counts':dict(counts),
            'mass_coefficients':[1,2],'raw_state_coordinates':[0,1,2],
            'transport_scope':'All dimension-two positive families above, shear parameters -2,-1,1,2.',
            'scope':'Finite regression only. Not a substitute for the arbitrary real-space Lean theorem.',
            'independent_external_implementation':False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
