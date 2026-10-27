#!/usr/bin/env python3
"""Exact rational sanity checks, separate from the universal Lean proofs."""
from __future__ import annotations
from fractions import Fraction as Q
import json


def matrix(rows):
    return tuple(tuple(Q(x) for x in row) for row in rows)


def mul(a, b):
    assert a and b and len(a[0]) == len(b)
    return tuple(tuple(sum((a[i][k]*b[k][j] for k in range(len(b))), Q(0))
                       for j in range(len(b[0]))) for i in range(len(a)))


def add(a, b):
    assert len(a) == len(b) and len(a[0]) == len(b[0])
    return tuple(tuple(x+y for x,y in zip(ar,br)) for ar,br in zip(a,b))


def sub(a, b):
    return add(a, tuple(tuple(-x for x in r) for r in b))


def eye(n):
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def power(a,n):
    r=eye(len(a))
    for _ in range(n): r=mul(r,a)
    return r


def coarse(c,t,r):
    return mul(c,mul(t,r))


def defect(c,r,s,t):
    return sub(coarse(c,mul(s,t),r),mul(coarse(c,s,r),coarse(c,t,r)))


def main():
    checks=[]
    # Same exact three-coordinate cycle as the Lean example.
    c=matrix([[1,0,0]]); r=matrix([[1],[0],[0]])
    t=matrix([[0,1,0],[0,0,1],[1,0,0]])
    values=[coarse(c,power(t,n),r)[0][0] for n in range(7)]
    assert values == list(map(Q,[1,0,0,1,0,0,1]))
    checks.append({'name':'delayed return', 'coarse_powers_0_through_6':[str(x) for x in values]})
    # Deliberately nonsymmetric operators test orientation and signs.
    s=matrix([[1,2,3],[0,-1,4],[5,0,2]])
    u=matrix([[2,0,-1],[3,1,0],[0,4,1]])
    h=sub(eye(3),mul(r,c))
    assert defect(c,r,s,t) == mul(c,mul(s,mul(h,mul(t,r))))
    checks.append({'name':'hidden-return factorization','passed':True})
    lhs=add(mul(defect(c,r,s,t),coarse(c,u,r)),defect(c,r,mul(s,t),u))
    rhs=add(mul(coarse(c,s,r),defect(c,r,t,u)),defect(c,r,s,mul(t,u)))
    assert lhs == rhs
    checks.append({'name':'defect coherence','passed':True})
    c1=matrix([[1,0,0],[0,1,0]]); r1=matrix([[1,0],[0,1],[0,0]])
    c2=matrix([[1,0]]); r2=matrix([[1],[0]])
    lhs=defect(mul(c2,c1),mul(r1,r2),s,t)
    rhs=add(coarse(c2,defect(c1,r1,s,t),r2),
            defect(c2,r2,coarse(c1,s,r1),coarse(c1,t,r1)))
    assert lhs == rhs
    checks.append({'name':'two-stage defect','passed':True})
    a=matrix([[1],[1]]); syn=matrix([[1,0]]); e=mul(a,syn)
    k=mul(a,mul(matrix([[3]]),syn))
    assert mul(e,mul(k,e)) == k and mul(syn,mul(k,a)) == matrix([[3]])
    assert mul(e,matrix([[0],[1]])) != matrix([[0],[1]])
    checks.append({'name':'redundant resolution','passed':True})
    print(json.dumps({'passed':True,'arithmetic':'fractions.Fraction',
                      'checks':checks,
                      'scope':'Five fixed sanity checks; not evidence for universal generalization.'},indent=2))

if __name__ == '__main__': main()
