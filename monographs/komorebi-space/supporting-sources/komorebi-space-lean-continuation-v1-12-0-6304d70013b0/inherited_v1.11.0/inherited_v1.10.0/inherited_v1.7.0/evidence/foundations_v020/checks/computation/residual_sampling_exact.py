#!/usr/bin/env python3
"""Exact rational audit of block residual accumulation and repair naturality.

Independent finite matrix implementation. This does not prove the infinite
Lean results. No floating-point arithmetic, random sampling, or network access.
"""
from __future__ import annotations
import argparse, hashlib, json, platform, sys, time
from fractions import Fraction as Q
from pathlib import Path

Matrix = tuple[tuple[Q, ...], ...]
assertions = 0

def check(ok: bool, label: str) -> None:
    global assertions
    assertions += 1
    if not ok:
        raise AssertionError(label)

def mat(h: int, w: int, f) -> Matrix:
    return tuple(tuple(Q(f(i,j)) for j in range(w)) for i in range(h))

def zero(h: int, w: int) -> Matrix:
    return mat(h,w,lambda i,j:0)

def eye(n: int) -> Matrix:
    return mat(n,n,lambda i,j:int(i==j))

def add(a: Matrix,b: Matrix) -> Matrix:
    assert len(a)==len(b) and len(a[0])==len(b[0])
    return mat(len(a),len(a[0]),lambda i,j:a[i][j]+b[i][j])

def neg(a: Matrix) -> Matrix:
    return mat(len(a),len(a[0]),lambda i,j:-a[i][j])

def sub(a: Matrix,b: Matrix) -> Matrix:
    return add(a,neg(b))

def mul(a: Matrix,b: Matrix) -> Matrix:
    assert len(a[0])==len(b)
    return mat(len(a),len(b[0]),lambda i,j:sum((a[i][k]*b[k][j] for k in range(len(b))),Q(0)))

def norm(a: Matrix) -> Q:
    # Operator norm for real finite-dimensional sup norms, evaluated rationally.
    return max(sum((abs(x) for x in row),Q(0)) for row in a)

def data(h: int,w: int,seed: int, contractive: bool=False) -> Matrix:
    a=mat(h,w,lambda i,j:Q(((seed+3)*(i+2)+(seed+5)*(j+1)+i*j)%9-4,4))
    scale=max(Q(1),norm(a)) if contractive else Q(1)
    return mat(h,w,lambda i,j:a[i][j]/scale)

def restrict(downs: list[Matrix],dims: list[int],i: int,j: int) -> Matrix:
    out=eye(dims[i])
    for k in range(i,j):
        out=mul(out,downs[k])
    return out

def residual(dx: list[Matrix],dy: list[Matrix],f: list[Matrix]) -> list[Matrix]:
    return [sub(mul(dy[n],f[n+1]),mul(f[n],dx[n])) for n in range(len(dx))]

def block_recursive(dx,dy,x,y,r,i,j):
    out=zero(y[i],x[i])
    left=eye(y[i])
    for k in range(i,j):
        out=add(mul(left,r[k]),mul(out,dx[k]))
        left=mul(left,dy[k])
    return out

def block_closed(dx,dy,x,y,r,i,j):
    out=zero(y[i],x[j])
    for k in range(i,j):
        out=add(out,mul(mul(restrict(dy,y,i,k),r[k]),restrict(dx,x,k+1,j)))
    return out

def trial(depth: int, seed: int, schedule: list[int]) -> None:
    x=[1+(n+seed)%3 for n in range(depth+1)]
    y=[1+(2*n+seed)%4 for n in range(depth+1)]
    dx=[data(x[n],x[n+1],seed+11*n,True) for n in range(depth)]
    dy=[data(y[n],y[n+1],seed+7*n+3,True) for n in range(depth)]
    f=[data(y[n],x[n],seed+5*n+4) for n in range(depth+1)]
    d=residual(dx,dy,f)
    r=[data(y[n],x[n+1],seed+13*n+6) for n in range(depth)]
    check(all(norm(a)<=1 for a in dx+dy),'contractive bonds')
    for i in range(depth+1):
        for j in range(i,depth+1):
            b=block_closed(dx,dy,x,y,d,i,j)
            actual=sub(mul(restrict(dy,y,i,j),f[j]),mul(f[i],restrict(dx,x,i,j)))
            check(b==actual,'actual block differential')
            check(b==block_recursive(dx,dy,x,y,d,i,j),'independent telescope')
            z=block_closed(dx,dy,x,y,r,i,j)
            check(z==block_recursive(dx,dy,x,y,r,i,j),'arbitrary residual telescope')
            check(norm(z)<=sum((norm(r[k]) for k in range(i,j)),Q(0)),'local norm sum')
            check(norm(z)<=Q(j-i)*max((norm(a) for a in r),default=Q(0)),'uniform block bound')
    cdx=[restrict(dx,x,i,j) for i,j in zip(schedule,schedule[1:])]
    cdy=[restrict(dy,y,i,j) for i,j in zip(schedule,schedule[1:])]
    sf=[f[n] for n in schedule]
    ds=residual(cdx,cdy,sf)
    cd=[block_closed(dx,dy,x,y,d,i,j) for i,j in zip(schedule,schedule[1:])]
    check(ds==cd,'d_sample S = C d')
    check(max(map(norm,sf))<=max(map(norm,f)),'sample contractive')
    gap=max((j-i for i,j in zip(schedule,schedule[1:])),default=0)
    check(max(map(norm,cd),default=Q(0))<=gap*max(map(norm,d)),'residual sample bound')
    for i,j,k in zip(schedule,schedule[1:],schedule[2:]):
        big=block_closed(dx,dy,x,y,d,i,k)
        pasted=add(mul(restrict(dy,y,i,j),block_closed(dx,dy,x,y,d,j,k)),
                   mul(block_closed(dx,dy,x,y,d,i,j),restrict(dx,x,j,k)))
        check(big==pasted,'block concatenation')

def repair_trial(seed: int) -> None:
    d=mat(1,3,lambda i,j:int(j==2))
    D=mat(2,4,lambda i,j:int(j==i+2))
    A=mat(3,1,lambda i,j:Q(seed+i-2,3) if i<2 else 1)
    B=mat(4,2,lambda i,j:Q((seed+2*i+j)%5-2,3) if i<2 else int(i-2==j))
    C=data(2,1,seed+3)
    H=data(2,1,seed+6)
    L=data(2,2,seed+9)
    S=mat(4,3,lambda i,j:(L[i][j] if j<2 else H[i][0]) if i<2 else
          (0 if j<2 else C[i-2][0]))
    PA=sub(eye(3),mul(A,d));PB=sub(eye(4),mul(B,D))
    mismatch=sub(mul(S,A),mul(B,C))
    check(mul(d,A)==eye(1),'source section')
    check(mul(D,B)==eye(2),'target section')
    check(mul(D,S)==mul(C,d),'cochain square')
    check(mul(D,mismatch)==zero(2,1),'mismatch is exact-valued')
    check(sub(mul(PB,S),mul(S,PA))==mul(mismatch,d),'repair route difference')
    check(norm(mismatch)<=norm(S)*norm(A)+norm(B)*norm(C),'mismatch gain bound')
    for k in range(4):
        f=data(3,1,seed+k)
        err=sub(mul(PB,mul(S,f)),mul(S,mul(PA,f)))
        check(norm(err)<=norm(mismatch)*norm(mul(d,f)),'pointwise repair bound')
        exact=data(2,1,seed+2*k)
        r=data(1,1,seed+3*k)
        e=mat(3,1,lambda i,j:exact[i][0] if i<2 else 0)
        z=add(e,mul(A,r))
        lhs=mul(PB,mul(S,z))
        rhs=add(mul(S,e),mul(mismatch,r))
        check(lhs==rhs,'triangular exact coordinate')
        check(mul(D,mul(S,z))==mul(C,r),'triangular residual coordinate')

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();start=time.monotonic(); cases=0
    for depth in (2,3,5,8,12):
        for seed in range(6):
            schedules=[list(range(depth+1)),sorted(set([0,depth]+list(range(0,depth+1,2)))),
                       [0,0,depth],list(range(1,depth+1))]
            for schedule in schedules:
                trial(depth,seed,schedule);cases+=1
    for seed in range(24): repair_trial(seed)
    for m in range(1,33):
        x=y=[1]*(m+1);dx=dy=[eye(1)]*m;r=[eye(1)]*m
        check(norm(block_closed(dx,dy,x,y,r,0,m))==m,'sharp gain M')
        f=[mat(1,1,lambda i,j:Q(n)) for n in range(m+1)]
        check(max(map(norm,residual(dx,dy,f)))==1,'ramp adjacent residual')
        check(norm(sub(f[-1],f[0]))==m,'ramp coarse residual')
    # Mutations represent false claims or omitted transports, not proof checking.
    dx=dy=[eye(1),eye(1)];x=y=[1,1,1];f=[eye(1),mat(1,1,lambda i,j:2),eye(1)]
    d=residual(dx,dy,f)
    coarse=block_closed(dx,dy,x,y,d,0,2)
    dd=mat(1,2,lambda i,j:int(j==1))
    aa=mat(2,1,lambda i,j:int(i==1))
    bb=mat(2,1,lambda i,j:1)
    check(mul(dd,aa)==eye(1) and mul(dd,bb)==eye(1),'mutation fixture has two actual sections')
    p0=sub(eye(2),mul(aa,dd));p1=sub(eye(2),mul(bb,dd))
    rejects={
      'coarse_exact_implies_fine_exact': coarse==zero(1,1) and any(a!=zero(1,1) for a in d),
      'residual_is_just_subsampled': coarse!=d[0],
      'unconditional_repair_naturality': sub(p0,p1)!=zero(2,2),
    }
    for name,ok in rejects.items():check(ok,'reject '+name)
    result={'status':'PASS','arithmetic':'exact fractions over Q; sup operator norm by absolute row sums',
      'candidate_configurations':cases,'repair_map_configurations':24,'sharp_gain_values':list(range(1,33)),
      'positive_assertions':assertions-len(rejects),'mutation_rejections':rejects,
      'bounds':{'depths':[2,3,5,8,12],'seeds':list(range(6)),'dimension_X':'1+(n+seed)%3',
                'dimension_Y':'1+(2*n+seed)%4','schedules':['all stages','even plus endpoint','repeated initial then endpoint','skip initial']},
      'elapsed_seconds':time.monotonic()-start,'python_version':sys.version,'platform':platform.platform(),
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'nonclaims':['No infinite convergence or theorem is inferred from these tests.','No full pro-category or arbitrary-norm invariance.']}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return 0

if __name__=='__main__': raise SystemExit(main())
