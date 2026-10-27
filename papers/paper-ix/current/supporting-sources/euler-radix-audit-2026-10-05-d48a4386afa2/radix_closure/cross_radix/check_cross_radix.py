#!/usr/bin/env python3
"""Exact mixed-radix/cutoff tests and actual triplication-defect jets.

No parameter search. All series checks use Fractions; actual Euler packets
use the inherited audited modular Bernoulli engine at two fixed indices.
"""
from pathlib import Path
from fractions import Fraction as F
from math import factorial, comb
import argparse, hashlib, json, platform, sys

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate'
sys.path.insert(0,str(SRC))
import fast_parameter_certificate as old
b=old.base

def mul(a,c,N):
    out=[F(0)]*(N+1)
    for i,x in enumerate(a):
        for j,y in enumerate(c[:N+1-i]): out[i+j]+=x*y
    return out
def add(*aa,N):
    return [sum((a[i] if i<len(a) else 0) for a in aa) for i in range(N+1)]
def scale(a,c):return [c*x for x in a]
def dil(a,m):return [x*m**i for i,x in enumerate(a)]
def sh(a,k,N):return [F(0)]*k+a[:N+1-k]
def inv(a,N):
    c=[1/a[0]]
    for n in range(1,N+1):c.append(-sum(a[i]*c[n-i] for i in range(1,min(n,len(a)-1)+1))/a[0])
    return c
def exact_tests():
    N=24
    cosh=[F(1,factorial(2*n)) for n in range(N+1)]
    euler=inv(cosh,N)
    ds=[F(2**(2*n+1),factorial(2*n+2)) for n in range(N+1)]
    beta=inv(ds,N)
    a=add(scale(beta,3),[0,4],N=N)
    trip=add(mul(mul(a,a,N),dil(beta,9),N),scale(mul(mul(beta,beta,N),beta,N),-9),N=N)
    assert not any(trip)
    radix_checks=[]
    for m,n in [(2,3),(3,5),(3,7)]:
        wm=mul(dil(cosh,m*m),euler,N)
        wn=mul(dil(cosh,n*n),euler,N)
        wmn=mul(dil(cosh,m*m*n*n),euler,N)
        assert mul(wm,dil(wn,m*m),N)==wmn
        assert mul(wn,dil(wm,n*n),N)==wmn
        radix_checks.append([m,n])
    odd_moment_checks=0
    ee=[euler[n]*factorial(2*n) for n in range(N+1)]
    for m in (3,5,7):
        w=[sum((-1)**j*(m-1-2*j)**(2*k) for j in range(m)) for k in range(N+1)]
        for n in range(N+1):
            assert ee[n]==sum(comb(2*n,2*k)*w[k]*m**(2*(n-k))*ee[n-k] for k in range(n+1))
            odd_moment_checks+=1
    cutoffs=[]
    for r in range(2,10):
        p=beta[:r]+[F(0)]*(N+1-r)
        A=add(scale(p,3),[0,4],N=N)
        pp9=dil(p,9)
        numer=add(mul(mul(A,A,N),pp9,N),scale(mul(mul(p,p,N),p,N),-9),N=N)
        assert not any(numer[:r])
        D=numer[r:]+[F(0)]*r
        Bt=beta[r:]+[F(0)]*r
        Bt9=dil(Bt,9)
        lin=add(mul(add(scale(mul(A,pp9,N),6),scale(mul(p,p,N),-27),N=N),Bt,N),scale(mul(mul(A,A,N),Bt9,N),9**r),N=N)
        quad=add(mul(add(scale(pp9,9),scale(p,-27),N=N),mul(Bt,Bt,N),N),scale(mul(mul(A,Bt,N),Bt9,N),6*9**r),N=N)
        cub=add(scale(mul(mul(Bt,Bt,N),Bt9,N),9**(r+1)),scale(mul(mul(Bt,Bt,N),Bt,N),-9),N=N)
        defect=add(D,lin,sh(quad,r,N),sh(cub,2*r,N),N=N)
        assert not any(defect[:N+1-r])
        assert D[0]==-9*(9**r-1)*beta[r]
        cutoffs.append({'r':r,'checked_tail_degrees':N-r+1,'constant':str(D[0])})
    return {'series_degree':N,'mixed_radix_pairs':radix_checks,'odd_moment_identities':odd_moment_checks,'triplication_identity':True,'full_cutoffs':cutoffs}

def rec(n,bits):
    n%=1<<bits
    v=b.v2(n,bits)
    return {'valuation_or_lower_bound':v,'is_lower_bound':v==bits,
            'unit_mod65536':str((n>>v)%65536) if v+16<=bits else None,'residue':str(n)}
def actual_case(T):
    P=210;bits=180;M=1<<P
    B=17659+(1<<18)*T;r=B*(1<<640)-161
    costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range((r.bit_count()-1)//3+1)]
    assert min(costs)==-154 and max(q for q,v in enumerate(costs) if v==-154)==161
    Q=(P+r.bit_count()-154-2)//3
    gam=b.gamma(r,-154,P,Q);src=list(b.source(P))
    def local(gg):
        lo,hi=old.local_split(P,10202,15,gg,src)
        return [(aa+bb)%M for aa,bb in zip(lo,hi)]
    g=local(gam);assert all(a%(1<<178)==0 for a in g)
    K=[a>>178 for a in g];dk=[i*K[i]//2 for i in range(1,len(K))]
    c=0;cbits=P-179
    for j in range(cbits):
        if b.ev(dk,c,1<<(j+1)):c+=1<<j
    assert c%128==20
    dd=[v*(pow(9,q,M)-pow(9,161,M))%M for q,v in enumerate(gam)]
    defect=local(dd)
    derivative=[i*defect[i]//(1<<15) for i in range(1,len(defect))]
    dg=[i*g[i]//(1<<15) for i in range(1,len(g))]
    assert b.ev(dg,c,1<<bits)==0
    v=b.ev(defect,c,1<<bits);dv=b.ev(derivative,c,1<<bits)
    assert b.v2(v,bits)==157 and b.v2(dv,bits)==158
    return {'T':str(T),'actual_terminal':161,'mu':-154,'packet_max':Q,'stationary_Z_bits':cbits,'stationary_Z':str(c),'delta_value':rec(v,bits),'delta_derivative':rec(dv,bits),'G_at_stationary_point':rec(b.ev(g,c,1<<bits),bits)}

def main(path):
    exact=exact_tests()
    b.B=b.bernoullis(256);b.twoB=old.fast_twoB
    cases=[actual_case(T) for T in (0,22831001499602523078606181325)]
    result={'status':'passed','exact_checks':exact,'actual_cases':cases,'python':platform.python_version(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'nonclaims':['No actual singular Euler index','No universal nonvanishing','Odd-radix covariance does not imply shifted-jet zero propagation','No Lean run']}
    Path(path).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'passed','exact_checks':exact,'actual_cases':cases},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);main(p.parse_args().out)
