"""Exact finite teaching models for Paper I. All algebra is over Q unless noted.

These are independent explanatory examples, not newly Lean-certified declarations.
No random data, numerical rank tolerance, or external service is used.
"""
from __future__ import annotations
from collections.abc import Sequence
import sympy as sp


def unit(n: int, j: int) -> sp.Matrix:
    if not 0 <= j < n:
        raise ValueError('Basis index out of range')
    return sp.eye(n)[:, j]


def matrix_unit(n: int, i: int, j: int) -> sp.Matrix:
    return unit(n, i) * unit(n, j).T


def chain(n: int) -> sp.Matrix:
    """Forward nilpotent chain: e_j -> e_(j+1), last vector -> 0."""
    a = sp.zeros(n)
    for j in range(n-1):
        a[j+1, j] = 1
    return a


def column_basis(a: sp.Matrix) -> sp.Matrix:
    cols = a.columnspace()
    return sp.Matrix.hstack(*cols) if cols else sp.zeros(a.rows, 0)


def orbit(ops: Sequence[sp.Matrix], seeds: Sequence[sp.Matrix], n: int):
    """Exact ascending invariant-span iteration, including the equality stop step."""
    if any(o.shape != (n,n) for o in ops) or any(s.shape != (n,1) for s in seeds):
        raise ValueError('Operator or seed type mismatch')
    w = column_basis(sp.Matrix.hstack(*seeds)) if seeds else sp.zeros(n,0)
    history = [w.cols]
    for _ in range(n+1):
        q = column_basis(sp.Matrix.hstack(w, *(o*w for o in ops)))
        history.append(q.cols)
        if q.cols == w.cols:
            return q, history
        w = q
    raise AssertionError('Exact ascending subspace iteration exceeded its dimension bound')


def krylov(a: sp.Matrix, seeds: Sequence[sp.Matrix], steps: int | None = None):
    steps = a.rows if steps is None else steps
    return sp.Matrix.hstack(*(a**j * s for j in range(steps) for s in seeds))


def poly_matrix(p, a: sp.Matrix, t):
    p = sp.Poly(p, t)
    out = sp.zeros(a.rows)
    for (i,), c in p.terms():
        out += c * a**i
    return out


def path(n: int) -> sp.Matrix:
    a = sp.zeros(n)
    for j in range(n-1):
        a[j,j+1] = a[j+1,j] = 1
    return a


def cycle(n: int) -> sp.Matrix:
    if n < 3:
        raise ValueError('A simple cycle has at least three vertices')
    a = sp.zeros(n)
    for j in range(n):
        a[j,(j-1)%n] = a[j,(j+1)%n] = 1
    return a


def data():
    j = chain(3)
    n = sp.diag(j,j)
    s = unit(6,0) + unit(6,3)
    pe = sp.diag(1,1,1,0,0,0)
    pf = sp.eye(6)-pe
    q = sp.Matrix.vstack(unit(6,0).T,unit(6,3).T)
    ur = sp.Matrix([[0,-1],[1,0]])
    inc = sp.Matrix([[1,0],[0,1],[0,0]])
    ret = inc.T
    tr = sp.diag(ur,sp.zeros(3))
    ta = sp.zeros(5); ta[2:5,0:2] = inc
    tb = sp.zeros(5); tb[0:2,2:5] = ret
    pu = sp.diag(1,1,0,0,0); pv=sp.eye(5)-pu
    shear = sp.Matrix([[1,1],[0,1]])
    p = shear*sp.diag(1,0)*shear.inv(); qc=sp.eye(2)-p
    tt = sp.Matrix([[1,2,0],[0,1,3],[4,0,1]])
    cancel = sp.Matrix([[0,0,0,0],[1,0,0,0],[1,0,0,0],[0,1,-1,0]])
    vs = [sp.Matrix([[1,0,0,0,0],[0,1,0,0,0]]),
          sp.Matrix([[0,0,1,0,0],[0,0,0,1,0]]),
          sp.Matrix([[0,0,0,0,1],[0,0,0,0,0]])]
    w=sp.Matrix([[1,2,3,4,5],[6,7,8,9,10]])
    mult=[w[:,0:2],w[:,2:4],sp.Matrix.hstack(w[:,4],sp.zeros(2,1))]
    t=sp.Symbol('t'); sep=sp.diag(j,2*sp.eye(3)+j)
    p2=(3*t**5-15*t**4+20*t**3)/16
    a6=cycle(6)
    cq=sp.Matrix([[2,1,-1,-2,-1,1],[0,1,1,0,-1,-1]])
    return dict(J=j,N=n,s=s,Pe=pe,Pf=pf,Q=q,R=ur,A=inc,B=ret,
                typed_ops=[tr,ta,tb,pu,pv],typed_R=tr,typed_A=ta,typed_B=tb,
                PU=pu,PV=pv,U=shear,P=p,Qob=qc,x=sp.Matrix([3,2]),T=tt,
                D=cancel,Vs=vs,W=w,As=mult,t=t,Tsep=sep,p2=p2,p0=1-p2,
                path5=path(5),cycle6=a6,cycle_Q=cq)


def serial(a):
    if isinstance(a,sp.MatrixBase):
        return [[str(x) for x in row] for row in a.tolist()]
    return str(a)
