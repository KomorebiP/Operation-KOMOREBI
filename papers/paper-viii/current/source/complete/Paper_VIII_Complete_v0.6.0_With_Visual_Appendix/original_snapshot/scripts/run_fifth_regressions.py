#!/usr/bin/env python3
"""Independent finite mirrors of Paper VIII block-five constructions.

Author: Komorebi P.
Exact checks use Fraction; NumPy is used only in the separately marked numerical
checks. These are not executions of Lean definitions and not theorem proofs.
Existing reports are never overwritten unless --overwrite is explicit.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys
import time
from typing import Sequence

Matrix = list[list[F]]

def eye(n: int) -> Matrix:
    return [[F(i == j) for j in range(n)] for i in range(n)]

def zeros(n: int, m: int) -> Matrix:
    return [[F(0) for _ in range(m)] for _ in range(n)]

def mm(a: Matrix, b: Matrix) -> Matrix:
    if not a:
        return []
    if not b:
        raise ValueError('Empty inner matrix requires explicit shape')
    if len(a[0]) != len(b):
        raise ValueError('Matrix dimensions do not match')
    return [[sum((x*y for x, y in zip(row, col)), F(0))
             for col in zip(*b)] for row in a]

def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]

def plus(a: Matrix, b: Matrix, sign: int = 1) -> Matrix:
    return [[x + sign*y for x,y in zip(ar,br)] for ar,br in zip(a,b)]

def inverse(a: Matrix) -> Matrix:
    n = len(a)
    if any(len(row) != n for row in a):
        raise ValueError('Inverse requires square matrix')
    w = [row[:] + identity for row,identity in zip(a,eye(n))]
    for k in range(n):
        pivot = next((i for i in range(k,n) if w[i][k]), None)
        if pivot is None:
            raise ValueError('Singular matrix')
        w[k], w[pivot] = w[pivot], w[k]
        t = w[k][k]
        w[k] = [x/t for x in w[k]]
        for i in range(n):
            if i != k:
                t = w[i][k]
                w[i] = [x-t*y for x,y in zip(w[i],w[k])]
    result = [row[n:] for row in w]
    assert mm(a,result) == eye(n)
    return result

def block(a: Matrix, rows: Sequence[int], cols: Sequence[int]) -> Matrix:
    return [[a[i][j] for j in cols] for i in rows]

def nonzero(a: Matrix) -> bool:
    return any(x for row in a for x in row)

def frob2(a: Matrix) -> F:
    return sum((x*x for row in a for x in row), F(0))

def closure(n: int, edges: set[tuple[int,int]]) -> list[list[bool]]:
    r = [[i == j or (i,j) in edges for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                r[i][j] = r[i][j] or (r[i][k] and r[k][j])
    return r

def levels(n: int, edges: set[tuple[int,int]]) -> list[int]:
    predecessors = [{a for a,b in edges if b == v} for v in range(n)]
    pending = set(range(n)); out = [0]*n
    while pending:
        ready = {v for v in pending if not (predecessors[v] & pending)}
        if not ready:
            raise ValueError('Cyclic task graph')
        for v in ready:
            out[v] = 1 + max((out[u] for u in predecessors[v]), default=0)
        pending -= ready
    return out

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--seed', type=int, default=202609065)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = args.out or root/'verification'/('fifth_examples_'+stamp)/'SUMMARY.json'
    if out.exists() and not args.overwrite:
        parser.error('Output already exists; choose a fresh path or use --overwrite')
    rng = random.Random(args.seed); start=time.monotonic()
    counts: dict[str,int] = {}
    report: dict = {'started_utc':stamp,'seed':args.seed,'pass':False,
      'kind':'independent finite regression mirrors, not Lean executions',
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    try:
        import numpy as np
        # Exact band-address enumeration, including diagonal and saturated endpoints.
        c=0
        for p in range(1,41):
            for w in range(p):
                size=sum(abs(i-j)<=w for i in range(p) for j in range(p))
                assert size==p*(2*w+1)-w*(w+1)
                for b,q in [(0,3),(1,0),(2,3)]:
                    # Explicit addresses, not just comparison of copied formulas.
                    if p<=8:
                        addresses=[(i,j,u,v) for i in range(p) for j in range(p)
                                   if abs(i-j)<=w for u in range(b) for v in range(b)]
                        assert len(addresses)==b*b*size
                        assert len(addresses)*q*2==2*q*b*b*size
                c+=1
        counts['band_address_cases_exact']=c
        # Independent levels, actual paths and exhaustive scheduling for small graphs.
        c=brute=0
        for n in range(8):
            for rep in range(25):
                order=list(range(n));rng.shuffle(order)
                edges={(order[i],order[j]) for i in range(n) for j in range(i+1,n)
                       if rng.random()<.35}
                lev=levels(n,edges);dep=max(lev,default=0)
                assert all(lev[u]<lev[v] for u,v in edges)
                path_lengths=[]
                def visit(path: list[int]) -> None:
                    path_lengths.append(len(path))
                    for a,b in edges:
                        if a==path[-1]:
                            assert b not in path
                            visit(path+[b])
                for v in range(n):visit([v])
                assert dep==max(path_lengths,default=0)
                if n<=4:
                    best=n
                    for s in product(range(1,n+1),repeat=n):
                        if all(s[u]<s[v] for u,v in edges):
                            assert all(lev[v]<=s[v] for v in range(n))
                            best=min(best,max(s,default=0))
                    assert dep==best;brute+=1
                # Dependent unequal blocks, with actual local inverse and transfers.
                dims=[rng.randrange(1,3) for _ in range(n)]
                diagonals=[];dinv=[];rhs=[]
                for d in dims:
                    a=[[F(rng.randrange(1,4)) if i==j else
                        F(rng.randrange(-2,3)) if i<j else F(0)
                        for j in range(d)] for i in range(d)]
                    diagonals.append(a);dinv.append(inverse(a))
                    rhs.append([[F(rng.randrange(-4,5))] for _ in range(d)])
                t={(b,a):[[F(rng.randrange(-2,3)) for _ in range(dims[a])]
                           for _ in range(dims[b])] for a,b in edges}
                x=[zeros(d,1) for d in dims]
                for stage in range(1,dep+1):
                    old=[list(map(list,a)) for a in x]
                    for v in range(n):
                        if lev[v]==stage:
                            y=rhs[v]
                            for u,b in edges:
                                if b==v:y=plus(y,mm(t[v,u],old[u]),-1)
                            x[v]=mm(dinv[v],y)
                for v in range(n):
                    y=mm(diagonals[v],x[v])
                    for u,b in edges:
                        if b==v:y=plus(y,mm(t[v,u],x[u]))
                    assert y==rhs[v]
                c+=1
        counts['dag_and_staged_triangular_cases_exact']=c
        counts['exhaustive_minimum_schedule_cases']=brute
        for n in range(1,9):
            try:levels(n,{(v,(v+1)%n) for v in range(n)})
            except ValueError:pass
            else:raise AssertionError('Cycle not rejected')
        counts['cycle_rejections']=8
        # Actual exact inverses on possibly cyclic supports, with unequal packet widths.
        inverse_cases=schur_cases=missing_inverse=missing_schur=0
        for p in range(1,7):
            for rep in range(10):
                widths=[rng.randrange(1,3) for _ in range(p)]
                off=[0]
                for d in widths:off.append(off[-1]+d)
                parts=[list(range(off[i],off[i+1])) for i in range(p)]
                n=off[-1];a=zeros(n,n)
                for b in range(p):
                    for src in range(p):
                        if b==src or rng.random()<.28:
                            for i in parts[b]:
                                for j in parts[src]:a[i][j]=F(rng.randrange(-2,3))
                for i in range(n):a[i][i]=1+sum(abs(a[i][j]) for j in range(n) if j!=i)
                ai=inverse(a)
                edges={(src,b) for src in range(p) for b in range(p)
                       if nonzero(block(a,parts[b],parts[src]))}
                reach=closure(p,edges)
                for src in range(p):
                    for b in range(p):
                        if not reach[src][b]:
                            assert not nonzero(block(ai,parts[b],parts[src]));missing_inverse+=1
                inverse_cases+=1
                if p<2:continue
                # Split packets; hidden identity connectivity includes a length-zero route.
                hcount=max(1,p//2);hs=list(range(hcount));rs=list(range(hcount,p))
                hi=[i for h in hs for i in parts[h]];ri=[i for r in rs for i in parts[r]]
                h=block(a,hi,hi);hinv=inverse(h)
                s=plus(block(a,ri,ri),mm(mm(block(a,ri,hi),hinv),block(a,hi,ri)),-1)
                hreach=closure(hcount,{(u,v) for u,v in edges if u in hs and v in hs})
                ridx={old:k for k,old in enumerate(ri)}
                for src in rs:
                    for b in rs:
                        route=(src,b) in edges or any((src,j) in edges and hreach[j][k]
                                  and (k,b) in edges for j in hs for k in hs)
                        if not route:
                            assert not nonzero(block(s,[ridx[i] for i in parts[b]],
                                                     [ridx[i] for i in parts[src]]))
                            missing_schur+=1
                schur_cases+=1
        counts.update(inverse_support_cases_exact=inverse_cases,
          inverse_missing_route_blocks_checked=missing_inverse,
          schur_support_cases_exact=schur_cases,schur_missing_route_blocks_checked=missing_schur)
        # Explicit cancellation: a directed route is permission, not nonzero inverse support.
        a=[[F(1),F(1),F(1)],[F(0),F(1),F(1)],[F(0),F(0),F(1)]]
        assert inverse(a)[0][2]==0 and a[0][2]!=0
        counts['allowed_route_cancellation_controls']=1
        # Non-coordinate rational orthogonal projector families via Householder conjugation.
        exact=0;frob_err=op_gap=0.0
        for n in range(1,7):
            for rep in range(12):
                v=[F(rng.randrange(-3,4)) for _ in range(n)]
                if not any(v):v[0]=F(1)
                vv=sum(x*x for x in v)
                u=[[F(i==j)-2*v[i]*v[j]/vv for j in range(n)] for i in range(n)]
                assert mm(transpose(u),u)==eye(n)
                groups=min(n,1+rep%3)
                projectors=[]
                for g in range(groups):
                    d=[[F(i==j and i%groups==g) for j in range(n)] for i in range(n)]
                    projectors.append(mm(mm(u,d),transpose(u)))
                a=[[F(rng.randrange(-3,4)) for _ in range(n)] for _ in range(n)]
                diagonal=zeros(n,n);total=F(0);terms=[]
                for b,pb in enumerate(projectors):
                    for j,pj in enumerate(projectors):
                        term=mm(mm(pb,a),pj)
                        if b==j:diagonal=plus(diagonal,term)
                        else:total+=frob2(term);terms.append(term)
                residual=plus(a,diagonal,-1)
                assert frob2(residual)==total;exact+=1
                rr=np.array(residual,dtype=float)
                left=float(np.linalg.norm(rr,2))
                right=sum(float(np.linalg.norm(np.array(t,dtype=float),2)) for t in terms)
                assert left<=right+1e-10
                op_gap=max(op_gap,left-right)
        counts['noncoordinate_discovery_cases_exact']=exact
        # Complex unitary changes of coordinates, separately numerical.
        gen=np.random.default_rng(args.seed)
        for n in range(1,9):
            for rep in range(8):
                raw=gen.normal(size=(n,n))+1j*gen.normal(size=(n,n))
                u,_=np.linalg.qr(raw)
                a=gen.normal(size=(n,n))+1j*gen.normal(size=(n,n))
                ps=[np.outer(u[:,j],u[:,j].conj()) for j in range(n)]
                rr=a-sum((p@a@p for p in ps),np.zeros_like(a))
                ts=[pb@a@pa for b,pb in enumerate(ps) for j,pa in enumerate(ps) if b!=j]
                err=abs(float(np.linalg.norm(rr,'fro')**2)-sum(float(np.linalg.norm(t,'fro')**2) for t in ts))
                assert err<1e-9;frob_err=max(frob_err,err)
        counts['complex_discovery_cases_numerical']=64
        # Actual positive matrix square roots, conditioned perturbed matrices and inverses.
        cond_violation=white_err=0.;jc=0
        for n in range(1,9):
            for rep in range(15):
                z=gen.normal(size=(n,n))+1j*gen.normal(size=(n,n))
                d=z.conj().T@z+np.eye(n)
                vals,q=np.linalg.eigh(d)
                sqrt_d=(q*np.sqrt(vals))@q.conj().T
                invsqrt=(q*(1/np.sqrt(vals)))@q.conj().T
                z=gen.normal(size=(n,n))+1j*gen.normal(size=(n,n))
                e=(z+z.conj().T)/2
                eta=[0.,.05,.2,.6,.95][rep%5]
                e=e*(eta/np.linalg.norm(e,2)) if eta else np.zeros_like(e)
                k=sqrt_d@e@sqrt_d
                a=d+k;normal=invsqrt@a@invsqrt
                assert np.linalg.eigvalsh(a).min()>0
                white_err=max(white_err,float(np.linalg.norm(invsqrt@d@invsqrt-np.eye(n),2)))
                cond=float(np.linalg.norm(normal,2)*np.linalg.norm(np.linalg.inv(normal),2))
                bound=(1+eta)/(1-eta)
                assert 1-1e-10<=cond<=bound+1e-8
                cond_violation=max(cond_violation,cond-bound)
                factor=lambda x:(np.sqrt(x)-1)/(np.sqrt(x)+1)
                assert factor(cond)<=factor(bound)+1e-10
                for steps in range(5):
                    assert factor(cond)**steps<=factor(bound)**steps+1e-10
                jc+=1
        counts['jacobi_square_root_and_factor_cases_numerical']=jc
        report.update(pass_=True,counts=counts,numerical_maxima={
          'complex_frobenius_squared_identity_absolute_error':frob_err,
          'real_operator_certificate_positive_violation':max(op_gap,0.),
          'jacobi_condition_positive_violation':max(cond_violation,0.),
          'inverse_sqrt_normalization_operator_error':white_err},
          numpy_version=np.__version__)
        report['pass']=report.pop('pass_')
    except Exception as exc:
        report.update(counts=counts,error=f'{type(exc).__name__}: {exc}')
        raise
    finally:
        report['seconds']=round(time.monotonic()-start,3)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(report,indent=2))
    return 0 if report['pass'] else 1

if __name__=='__main__':
    sys.exit(main())
