#!/usr/bin/env python3
"""Exact bounded tests for the v0.9.0 intrinsic arithmetic exchange block.

This tests finite residue models and explicit matrix certificates. Infinite
cohomology, universal statements, and canonical derived comparison maps are
established by the separate written proofs, not inferred from finite counts.
No randomness, floating-point arithmetic, network access, or external writes.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
import time
from pathlib import Path
from typing import Iterable
import sympy as sp
from sympy.polys.matrices import DomainMatrix
from sympy.polys.matrices.normalforms import smith_normal_decomp


def require(test: bool, message: str) -> None:
    if not test:
        raise AssertionError(message)


def valuation(x: int, p: int) -> int:
    require(x != 0, 'valuation called on zero')
    a, x = 0, abs(x)
    while x % p == 0:
        x //= p
        a += 1
    return a


def rows(A: sp.Matrix) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(A[i, j]) for j in range(A.cols)) for i in range(A.rows))


def mv(A: tuple[tuple[int, ...], ...], v: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(sum(a*x for a,x in zip(row,v)) for row in A)


def kernels(A: tuple[tuple[int, ...], ...], cols: int, q: int) -> set[tuple[int, ...]]:
    return {v for v in itertools.product(range(q), repeat=cols)
            if all(x % q == 0 for x in mv(A,v))}


def cert(A: sp.Matrix):
    D, S, T = (x.to_Matrix() for x in smith_normal_decomp(DomainMatrix.from_Matrix(A).convert_to(sp.ZZ)))
    require(S*A*T == D, 'invalid Smith matrix equality')
    require(abs(int(S.det())) == abs(int(T.det())) == 1, 'Smith changes not unimodular')
    ds = [abs(int(D[i,i])) for i in range(min(A.shape)) if D[i,i] != 0]
    require(all(D[i,j] == 0 for i in range(A.rows) for j in range(A.cols) if i != j), 'not diagonal')
    require(all(ds[i+1] % ds[i] == 0 for i in range(len(ds)-1)), 'Smith divisibility failed')
    return D, S, T, ds


def exact_reductions(T: sp.Matrix, rank: int, q: int) -> set[tuple[int, ...]]:
    return {tuple(sum(int(T[i,j])*c[j-rank] for j in range(rank,T.cols)) % q for i in range(T.rows))
            for c in itertools.product(range(q),repeat=T.cols-rank)}


def image_over_zp(Srows, ds, w: tuple[int, ...], p: int) -> bool:
    sw = mv(Srows,w)
    return (all(sw[i] % (p**valuation(di,p)) == 0 for i,di in enumerate(ds))
            and all(x == 0 for x in sw[len(ds):]))


def check_kernel_families() -> dict:
    counts = dict(matrices=0, smith_certificates=0, matrix_level_cases=0,
                  enumerated_vectors=0, boundary_elements=0, precision_cases=0,
                  precision_vectors=0, sharpness_cases=0, transition_elements=0)
    levels = ((2,1),(2,2),(2,3),(3,1),(3,2))
    for entries in itertools.product(range(-2,3), repeat=4):
        A=sp.Matrix(2,2,entries); Ar=rows(A)
        D,S,T,ds=cert(A); Sr=rows(S); rank=len(ds)
        counts['matrices']+=1; counts['smith_certificates']+=1
        # Independent 2x2 determinantal-divisor check.
        g=math.gcd(*entries); det=abs(int(A.det()))
        expected=[] if g == 0 else ([abs(g),det//abs(g)] if det else [abs(g)])
        require(ds == expected, 'Smith data disagree with gcd/minor certificate')
        cache={}
        for p,n in levels:
            q=p**n; ker=kernels(Ar,2,q); cache[p,n]=ker
            exact=exact_reductions(T,rank,q)
            aa=[valuation(di,p) for di in ds]
            require(len(ker)==p**(n*(2-rank)+sum(min(a,n) for a in aa)), 'kernel length formula')
            require(exact <= ker, 'exact reductions not in modular kernel')
            counts['matrix_level_cases']+=1; counts['enumerated_vectors']+=q*q
            for v in ker:
                av=mv(Ar,v); w=tuple(x//q for x in av)
                require(image_over_zp(Sr,ds,w,p) == (v in exact), 'boundary-zero criterion')
                counts['boundary_elements']+=1
        for p in (2,3):
            h=max([valuation(di,p) for di in ds]+[0])
            for n in (1,2):
                m=n+h; qm=p**m; qn=p**n
                km=cache.get((p,m))
                if km is None: km=kernels(Ar,2,qm)
                target={tuple(x%qn for x in v) for v in km}
                require(target==exact_reductions(T,rank,qn),'finite-precision lifting equality')
                counts['precision_cases']+=1; counts['precision_vectors']+=qm*qm
                for v in km:
                    vn=tuple(x%qn for x in v)
                    wn=tuple(x//qn for x in mv(Ar,vn)); wm=tuple(x//qm for x in mv(Ar,v))
                    diff=tuple(a-p**(m-n)*b for a,b in zip(wn,wm))
                    # This stronger integer equation certifies boundary naturality.
                    z=tuple((a-b)//qn for a,b in zip(vn,v))
                    require(diff==mv(Ar,z),'boundary transition equation')
                    counts['transition_elements']+=1
            if h:
                n=h
                for c in range(h):
                    qn=p**n; qm=p**(n+c)
                    km=kernels(Ar,2,qm)
                    im={tuple(x%qn for x in v) for v in km}
                    require(im != exact_reductions(T,rank,qn),'claimed minimal delay not sharp')
                    counts['sharpness_cases']+=1
    require(counts['matrices']==625,'wrong exhaustive matrix population')
    return {'bounds':{'entries':[-2,2],'shape':[2,2],'levels':levels},**counts}


def companion_norm(m: int) -> sp.Matrix:
    d=m-1; A=sp.zeros(d)
    for j in range(d-1): A[j+1,j]=1
    for i in range(d): A[i,d-1]=-1
    return A


def check_norm_family() -> dict:
    certificates=[]
    for m in range(2,13):
        A=companion_norm(m); I=sp.eye(m-1)
        require(A**m==I, 'norm-quotient group relation')
        require(sum((A**i for i in range(m)),sp.zeros(m-1))==sp.zeros(m-1),'norm is not zero')
        D,S,T,ds=cert(A-I)
        require(ds==[1]*(m-2)+[m],'norm-quotient Smith data')
        certificates.append({'m':m,'rank':m-1,'diagonal':ds})
    # Explicit bounded residue enumeration, no automatic rank truncation.
    bounds=[(3,3,n) for n in range(1,4)]+[(4,2,n) for n in range(1,4)]+[(5,5,1),(2,2,4),(8,2,1)]
    vectors=0; records=[]
    for m,p,n in bounds:
        A=companion_norm(m); Ar=rows(A-sp.eye(m-1)); q=p**n
        ker=kernels(Ar,m-1,q)
        a=valuation(m,p); require(len(ker)==p**min(n,a),'norm modular invariants')
        vectors+=q**(m-1)
        records.append({'m':m,'p':p,'n':n,'invariant_count':len(ker)})
        if m==p==3:
            expected={(b*3**(n-1)%q,-b*3**(n-1)%q) for b in range(3)}
            require(ker==expected,'explicit C3 invariant vectors')
            nxt=kernels(Ar,2,3*q)
            require({tuple(x%q for x in v) for v in nxt}=={(0,0)},'C3 residual transition not zero')
    return {'smith_certificates':certificates,'residue_cases':records,'enumerated_vectors':vectors}


def intertwiner_matrix(A: sp.Matrix,B: sp.Matrix) -> sp.Matrix:
    # Column-major vectorization: B f - f A = 0.
    cols=[]
    for j in range(A.rows):
        for i in range(B.rows):
            E=sp.zeros(B.rows,A.rows); E[i,j]=1
            F=B*E-E*A
            cols.append(sp.Matrix([F[r,c] for c in range(F.cols) for r in range(F.rows)]))
    return sp.Matrix.hstack(*cols)


def check_intertwiners() -> dict:
    families={2:[sp.eye(1),sp.Matrix([[-1]]),sp.Matrix([[0,1],[1,0]]),sp.diag(1,-1)],
              3:[sp.eye(1),companion_norm(3),sp.eye(2)]}
    cases=0; vectors=0; lifts=0; records=[]
    for p, reps in families.items():
        for i,A in enumerate(reps):
            for j,B in enumerate(reps):
                require(A**p==sp.eye(A.rows) and B**p==sp.eye(B.rows),'invalid representation input')
                F=intertwiner_matrix(A,B); D,S,T,ds=cert(F); r=len(ds); Fr=rows(F)
                require(max([valuation(x,p) for x in ds]+[0])<=1,'group-order lifting bound')
                exact=exact_reductions(T,r,p)
                km=kernels(Fr,F.cols,p*p)
                require({tuple(x%p for x in v) for v in km}==exact,'intertwiner delay one')
                cases+=1; vectors+=(p*p)**F.cols
                if A.rows==B.rows:
                    Ti=T.inv(); d=A.rows
                    for v in exact:
                        fbar=sp.Matrix(d,d,lambda a,b:v[b*d+a])
                        if int(fbar.det())%p==0:continue
                        y=Ti*sp.Matrix(v)
                        yl=sp.Matrix([0 if u<r else int(y[u])%p for u in range(T.cols)])
                        vf=T*yl
                        f=sp.Matrix(d,d,lambda a,b:vf[b*d+a])
                        require(B*f==f*A,'constructed lift is not an intertwiner')
                        require(all(int(vf[u]-v[u])%p==0 for u in range(len(v))),'lift changes specified reduction')
                        require(int(f.det())%p!=0,'lift determinant not a p-adic unit')
                        lifts+=1
                records.append({'p':p,'source':i,'target':j,'matrix_shape':list(F.shape),'smith':ds})
    return {'pair_cases':cases,'enumerated_vectors':vectors,'verified_isomorphism_lifts':lifts,'certificates':records}


def mm(A,B,q):
    return (( (A[0]*B[0]+A[1]*B[2])%q, (A[0]*B[1]+A[1]*B[3])%q,
              (A[2]*B[0]+A[3]*B[2])%q, (A[2]*B[1]+A[3]*B[3])%q ))


def power(A,n,q):
    out=(1,0,0,1)
    for _ in range(n):out=mm(out,A,q)
    return out


def check_nonflat() -> dict:
    I=(1,0,0,1); Jswap=(0,1,1,0)
    actions=0; lifts=0; vectors=0; periodic_positions=0; cases=[]
    for p in (3,5,7):
        q=p*p
        for J in itertools.product(range(p),repeat=4):
            if (J[0]*J[3]-J[1]*J[2])%p==0:continue
            A=tuple((a+p*b)%q for a,b in zip(I,J))
            require(power(A,p,q)==I,'finite action relation failed')
            N=tuple(sum(power(A,i,q)[j] for i in range(p))%q for j in range(4))
            require(N==tuple(p*a for a in I),'cyclic norm formula failed')
            actions+=1
        J=Jswap; A=tuple(a+p*b for a,b in zip(I,J))
        Ar=((0,p),(p,0)); Nr=((p,0),(0,p))
        allv=list(itertools.product(range(q),repeat=2)); vectors+=len(allv)
        pm={(p*a,p*b) for a,b in itertools.product(range(p),repeat=2)}
        for degree in range(12):
            diff=Ar if degree%2==0 else Nr
            prev=Nr if degree%2==0 else Ar
            ker={v for v in allv if all(x%q==0 for x in mv(diff,v))}
            im={tuple(x%q for x in mv(prev,v)) for v in allv}
            require(ker==im==pm,'cyclic periodic exactness')
            periodic_positions+=1
        require(all(x%p==0 for v in pm for x in v),'H0 evaluation should reduce to zero')
        # Nonpositive free resolution for k over R: verify each repeated map.
        require({x for x in range(q) if p*x%q==0}=={p*x%q for x in range(q)},'Tor free resolution not exact')
        for B in itertools.product(range(p),repeat=4):
            At=tuple((a+q*b)%(p**3) for a,b in zip(A,B))
            rel=tuple((a-b)%(p**3) for a,b in zip(power(At,p,p**3),I))
            require(rel==tuple(q*b for b in Jswap),'lift-dependent relation residual')
            require(any(rel),'invalid relation lift accepted')
            lifts+=1
        cases.append({'p':p,'rank':2,'H0_order':p*p,'positive_cohomology_order':1,
                      'A':list(A),'all_matrix_lifts_tested':p**4})
    require(actions==sum((p*p-1)*(p*p-p) for p in (3,5,7)), 'GL2 enumeration count')
    # Boundary fixtures: invertibility of J and oddness of p are not cosmetic.
    q=4; A=(1,2,2,1); d=((0,2),(2,0)); N=((2,2),(2,2))
    vv=list(itertools.product(range(q),repeat=2))
    ker={v for v in vv if all(x%q==0 for x in mv(N,v))}
    im={tuple(x%q for x in mv(d,v)) for v in vv}
    require(len(ker)//len(im)==2,'p=2 boundary expected H1 of order 2')
    q=9; N=((3,0),(0,3))
    ker=kernels(N,2,q)
    require(len(ker)==9,'singular J=0 control should have nonzero H1')
    return {'all_invertible_J_cases':actions,'selected_module_vectors':vectors,
            'all_selected_matrix_lifts':lifts,'periodic_positions':periodic_positions,
            'selected_cases':cases,'excluded_case_H1_orders':{'p2_Jswap':2,'p3_Jzero':9},
            'nonclaim':'Finite checks do not compute an unbounded derived tensor by truncation. The full degree formula is proved in the manuscript.'}



def bar_matrix(A: sp.Matrix, order: int, degree: int, q: int) -> sp.Matrix:
    """Full inhomogeneous cochain differential for a cyclic group."""
    d=A.rows
    src=list(itertools.product(range(order),repeat=degree))
    dst=list(itertools.product(range(order),repeat=degree+1))
    index={g:i for i,g in enumerate(src)}
    out=sp.zeros(d*len(dst),d*len(src))
    powers=[(A**i).applyfunc(lambda x:int(x)%q) for i in range(order)]
    for z,g in enumerate(dst):
        first=g[1:]; mat=powers[g[0]]
        for a in range(d):
            for b in range(d):out[z*d+a,index[first]*d+b]+=mat[a,b]
        for i in range(1,degree+1):
            merged=g[:i-1]+((g[i-1]+g[i])%order,)+g[i+1:]
            for a in range(d):out[z*d+a,index[merged]*d+a]+=(-1)**i
        for a in range(d):out[z*d+a,index[g[:-1]]*d+a]+=(-1)**(degree+1)
    return out


def image_order_mod(A: sp.Matrix,q: int) -> int:
    D,S,T,ds=cert(A)
    return math.prod(q//math.gcd(di,q) for di in ds)


def check_bar_resolution() -> dict:
    fixtures=[('nonflat',sp.Matrix([[1,3],[3,1]]),9,(9,1,1)),
              ('reduced',sp.eye(2),3,(9,9,9)),
              ('norm_quotient',companion_norm(3),9,(3,3,3)),
              ('trivial',sp.eye(2),9,(81,9,9))]
    out=[]
    for name,A,q,expected in fixtures:
        diffs=[bar_matrix(A,3,j,q) for j in range(3)]
        for i in range(2):
            require(all(int(x)%q==0 for x in diffs[i+1]*diffs[i]),'bar differential does not square to zero')
        images=[image_order_mod(D,q) for D in diffs]
        kernels_=[q**D.cols//im for D,im in zip(diffs,images)]
        groups=(kernels_[0],kernels_[1]//images[0],kernels_[2]//images[1])
        require(groups==expected,'independent bar cohomology disagrees')
        out.append({'name':name,'q':q,'H0_H1_H2_orders':groups,'matrix_shapes':[list(D.shape) for D in diffs]})
    return {'fixtures':out,'smith_certificates':12,'chain_compositions_checked':8,
            'independence':'Full bar differentials, not the periodic cyclic resolution, with verified integer Smith changes.'}


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True); args=ap.parse_args()
    start=time.perf_counter()
    results={'status':'PASS','kernel':check_kernel_families(),'norm_quotient':check_norm_family(),
             'intertwiners':check_intertwiners(),'nonflat':check_nonflat(),'bar_resolution':check_bar_resolution(),
             'evidence':'exact bounded regression; general statements have written proofs, not Lean proofs',
             'environment':{'python':sys.version,'sympy':sp.__version__,'platform':platform.platform()},
             'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'argv':sys.argv,'elapsed_seconds':time.perf_counter()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))

if __name__=='__main__':main()
