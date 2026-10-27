#!/usr/bin/env python3
"""Independent finite regression mirrors, not execution of the Lean definitions.

Author: Komorebi P.
Rational checks use Fraction throughout. Fourier checks use floating-point complex
arithmetic and are explicitly empirical. No GPU benchmark is run.
"""
from __future__ import annotations
from fractions import Fraction as Q
from pathlib import Path
import hashlib, json, random, time, traceback
import numpy as np

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'verification/fourth_examples'
RNG = random.Random(20260906)
ZERO = Q(0)

def vector(n: int) -> list[Q]:
    return [Q(RNG.randint(-5, 5), RNG.randint(1, 5)) for _ in range(n)]

def matrix(n: int, m: int) -> list[list[Q]]:
    return [vector(m) for _ in range(n)]

def transpose(a: list[list[Q]]) -> list[list[Q]]:
    return [list(row) for row in zip(*a)]

def matvec(a: list[list[Q]], x: list[Q]) -> list[Q]:
    return [sum((aij*xj for aij,xj in zip(row,x,strict=True)), ZERO) for row in a]

def matmul(a: list[list[Q]], b: list[list[Q]]) -> list[list[Q]]:
    bt = transpose(b)
    return [[sum((x*y for x,y in zip(row,col,strict=True)),ZERO) for col in bt] for row in a]

def kron(a: list[list[Q]], b: list[list[Q]]) -> list[list[Q]]:
    return [[av*bv for av in ar for bv in br] for ar in a for br in b]

def tensor_apply(factors: list[list[list[Q]]], x: list[Q]) -> tuple[list[Q], int]:
    if not factors:
        assert len(x)==1
        return x[:],0
    a, tail = factors[0],factors[1:]
    d=len(a)
    if not d:
        assert not x
        return [],0
    width=len(x)//d
    slices=[tensor_apply(tail,x[j*width:(j+1)*width]) for j in range(d)]
    y=[sum((a[i][j]*slices[j][0][u] for j in range(d)),ZERO) for i in range(d) for u in range(width)]
    return y,sum(count for _,count in slices)+2*d*d*width

def tensor_matrix(factors: list[list[list[Q]]]) -> list[list[Q]]:
    a=[[Q(1)]]
    for factor in reversed(factors):a=kron(factor,a)
    return a

def walsh_apply(x: list[Q]) -> tuple[list[Q], int]:
    if len(x)==1:return x[:],0
    half=len(x)//2
    plus=[x[i]+x[half+i] for i in range(half)]
    minus=[x[i]-x[half+i] for i in range(half)]
    u,c=walsh_apply(plus);v,d=walsh_apply(minus)
    return u+v,c+d+len(x)

def clipped(s: list[Q], c: list[Q], m: list[Q], budget: Q) -> tuple[Q,list[Q]]:
    if not s or not(len(s)==len(c)==len(m)) or any(x<=0 for x in s+c+m):
        raise ValueError('Positive, equally sized nonempty vectors required')
    cap=sum((a*b for a,b in zip(s,m)),ZERO)
    if not 0<budget<=cap:raise ValueError('Budget must be in (0, capacity]')
    thresholds=sorted(set(m[i]*s[i]/c[i] for i in range(len(s))))
    intercept=ZERO;slope=sum(c,ZERO)
    for upper in thresholds:
        t=(budget-intercept)/slope
        if t<=upper:
            return t,[min(m[i],t*c[i]/s[i]) for i in range(len(s))]
        saturated=[i for i in range(len(s)) if m[i]*s[i]/c[i]==upper]
        intercept+=sum((s[i]*m[i] for i in saturated),ZERO)
        slope-=sum((c[i] for i in saturated),ZERO)
    raise AssertionError('No saturation segment found for a feasible budget')

def main() -> int:
    OUT.mkdir(parents=True,exist_ok=True)
    started=time.monotonic()
    report={'seed':20260906,'implementation':'Independent Python regression mirrors; not the compiled Lean functions',
      'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'gpu_benchmarks_rerun':False,'exact_rational':{},'floating_point_fourier':{},'pass':False}
    try:
        for case in range(180):
            m=case%5+1;n=(case//5)%5+1
            a=matrix(m,m);b=matrix(n,n);x=matrix(n,m)
            column=[x[i][j] for j in range(m) for i in range(n)]
            left=matvec(kron(a,b),column)
            right=matmul(matmul(b,x),transpose(a))
            assert left==[right[i][j] for j in range(m) for i in range(n)]
        report['exact_rational']['kronecker_instances']=180
        for case in range(120):
            d=case%4;k=(case//4)%5
            factors=[matrix(d,d) for _ in range(k)]
            x=vector(d**k)
            y,count=tensor_apply(factors,x)
            assert y==matvec(tensor_matrix(factors),x)
            assert count==2*k*d**(k+1)
        report['exact_rational']['tensor_instances']=120
        for case in range(96):
            k=case%7;x=vector(2**k)
            y,count=walsh_apply(x)
            h=tensor_matrix([[[Q(1),Q(1)],[Q(1),Q(-1)]] for _ in range(k)])
            assert y==matvec(h,x)
            z,_=walsh_apply(y)
            assert z==[2**k*v for v in x]
            assert count==k*2**k
        report['exact_rational']['walsh_instances']=96
        for case in range(240):
            n=case%16+1;c=vector(n);r=vector(n);x=vector(n)
            t=[[c[i-j] if j<=i else r[j-i] for j in range(n)] for i in range(n)]
            g=c+[ZERO]+list(reversed(r[1:]));padded=x+[ZERO]*n
            circ=[[g[(i-j)%(2*n)] for j in range(2*n)] for i in range(2*n)]
            assert matvec(circ,padded)[:n]==matvec(t,x)
        report['exact_rational']['toeplitz_instances']=240
        boundary=0
        for case in range(600):
            size=case%9+1
            s=[Q(RNG.randint(1,9),RNG.randint(1,5)) for _ in range(size)]
            c=[Q(RNG.randint(1,9),RNG.randint(1,5)) for _ in range(size)]
            m=[Q(RNG.randint(1,9),RNG.randint(1,5)) for _ in range(size)]
            cap=sum((si*mi for si,mi in zip(s,m)),ZERO)
            budget=cap if case%10==0 else cap*Q(RNG.randint(1,99),100)
            scale,opt=clipped(s,c,m,budget)
            assert scale>0 and all(0<v<=cap_i for v,cap_i in zip(opt,m))
            assert sum((si*v for si,v in zip(s,opt)),ZERO)==budget
            alternative=[mi*budget/cap for mi in m]
            support=sum((ci*(x/o-1) for ci,x,o in zip(c,alternative,opt)),ZERO)
            assert support<=0
            if budget==cap:
                assert opt==m
                assert [min(m[i],2*scale*c[i]/s[i]) for i in range(size)]==m
                boundary+=1
            for bad in [ZERO,-cap,2*cap]:
                try:clipped(s,c,m,bad)
                except ValueError:pass
                else:raise AssertionError('Infeasible budget accepted')
        report['exact_rational'].update(clipped_instances=600,endpoint_cases=boundary,
            infeasible_budget_rejections=1800)
        max_diag=max_unit=max_apply=0.0
        nrng=np.random.default_rng(20260906)
        for n in range(1,25):
            idx=np.arange(n);f=np.exp(-2j*np.pi*np.outer(idx,idx)/n)/np.sqrt(n)
            for _ in range(4):
                c=nrng.normal(size=n)+1j*nrng.normal(size=n)
                x=nrng.normal(size=n)+1j*nrng.normal(size=n)
                circ=c[(idx[:,None]-idx[None,:])%n]
                ev=np.sqrt(n)*(f@c)
                max_diag=max(max_diag,float(np.max(np.abs(circ-f.conj().T@np.diag(ev)@f))))
                max_unit=max(max_unit,float(np.max(np.abs(f.conj().T@f-np.eye(n)))))
                max_apply=max(max_apply,float(np.max(np.abs(circ@x-f.conj().T@(ev*(f@x))))))
        assert max(max_diag,max_unit,max_apply)<1e-10
        report['floating_point_fourier']={'instances':96,'lengths':'1 through 24',
            'absolute_error_threshold':1e-10,'maximum_diagonalization_error':max_diag,
            'maximum_unitarity_error':max_unit,'maximum_application_error':max_apply,
            'dtype':'complex128','scope':'Numerical regressions, not universal proof or FFT benchmark'}
        report['pass']=True
    except Exception:
        report['failure']=traceback.format_exc()
    report['seconds']=round(time.monotonic()-started,3)
    (OUT/'SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)
    return 0 if report['pass'] else 1

if __name__=='__main__':raise SystemExit(main())
