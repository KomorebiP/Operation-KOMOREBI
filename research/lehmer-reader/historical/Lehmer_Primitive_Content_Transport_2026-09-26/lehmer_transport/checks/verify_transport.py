#!/usr/bin/env python3
"""Exact finite audit of transfers, content decomposition and primitive residues."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from math import gcd, isqrt, prod
from pathlib import Path
import json
import sys

from packet_core import shell, weight, sector, involution, tau_triangular, tau_from_product, valuation
from exact_algebra import (rank,rref,nullspace,solve,matvec,matmul,transpose,
                           build_kernel,harmonic_operator,integer_primitive)


def chi(n):return 0 if n%5==0 else 1 if n%5 in (1,4) else -1
def prime(n):return n>1 and all(n%d for d in range(2,isqrt(n)+1))
def mobius(n):
    s=1;p=2
    while p*p<=n:
        if n%p==0:
            n//=p;s=-s
            if n%p==0:return 0
        p+=1
    return -s if n>1 else s
def enc(x):
    if isinstance(x,F):return [x.numerator,x.denominator]
    if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [enc(v) for v in x]
    return x
def values(v):return [sum(x**j for x in v) for j in range(2,6)]
def kernel_values(K,v):
    z=values(v)
    return [sum(c*prod(x**a for x,a in zip(z,e)) for e,c in q['terms']) for q in K]
def table(vs,K,k):
    rows=defaultdict(lambda:[0]*len(K));mass=defaultdict(int)
    for v in vs:
        key=sector(v,2**k) if k is not None else min(v,involution(v))
        w=weight(v);mass[key]+=w
        for j,x in enumerate(kernel_values(K,v)):rows[key][j]+=w*x
    keys=sorted(rows)
    return keys,[mass[k] for k in keys],[rows[k] for k in keys]


class Jet:
    """Independent second derivatives in x0..x3, with v4=-sum x_i."""
    def __init__(self,v,g=None,h=None):
        self.v=v;self.g=tuple(g or [0]*4);self.h=tuple(h or [0]*16)
    def __add__(self,o):
        if not isinstance(o,Jet):o=Jet(o)
        return Jet(self.v+o.v,[a+b for a,b in zip(self.g,o.g)],
                   [a+b for a,b in zip(self.h,o.h)])
    __radd__=__add__
    def __neg__(self):return self*(-1)
    def __sub__(self,o):return self+-o
    def __mul__(self,o):
        if not isinstance(o,Jet):o=Jet(o)
        return Jet(self.v*o.v,[a*o.v+self.v*b for a,b in zip(self.g,o.g)],
            [self.h[4*i+j]*o.v+self.v*o.h[4*i+j]
             +self.g[i]*o.g[j]+self.g[j]*o.g[i] for i in range(4) for j in range(4)])
    __rmul__=__mul__
    def __pow__(self,n):
        y=Jet(1)
        for _ in range(n):y=y*self
        return y


def direct_laplacian_checks(K):
    count=0
    for point in [(1,2,4,8),(0,1,2,-2),(3,-7,5,11)]:
        v=[Jet(x,[int(i==j) for j in range(4)]) for i,x in enumerate(point)]
        v.append(-sum(v))
        D=prod(v[i]-v[j] for i in range(5) for j in range(i+1,5))
        ss=[sum(x**j for x in v) for j in range(2,6)]
        powers=[[x**j for j in range(15)] for x in ss]
        for q in K:
            Q=sum(c*prod(powers[i][e[i]] for i in range(4)) for e,c in q['terms'])
            h=(D*Q).h
            assert 5*sum(h[5*i] for i in range(4))-sum(h)==0
            count+=1
    return count


def main(outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    stats=Counter();K=json.loads(Path('evidence/kernels_through20.json').read_text())
    generated=[]
    for d in [22,24,26,28]:
        new=build_kernel(d,shell,weight);K.extend(new)
        generated.append(dict(degree=d,count=len(new)))
    assert [x['count'] for x in generated]==[4,5,6,7]
    for q in K:
        assert not harmonic_operator({tuple(e):c for e,c in q['terms']})
        assert all(sum((i+2)*e[i] for i in range(4))==q['degree'] for e,c in q['terms'])
        stats['symbolic_harmonic_certificates']+=1
        for n in range(1,(12+q['degree'])//12+1):
            assert sum(weight(v)*kernel_values([q],v)[0] for v in shell(n))==0
            stats['valence_initial_zero_coefficients']+=1
    stats['independent_jet_laplacian_checks']=direct_laplacian_checks(K)
    (out/'kernels_through28.json').write_text(json.dumps(K,indent=2)+'\n')
    tau=tau_triangular(500)
    assert tau[:129]==tau_from_product(128)
    stats['independent_product_coefficients']=128
    primitive={};content_examples=[];coarse_fail=[];coarse_prime_checks=0
    # Full content and theta-kernel checks on 1..128. Coarse low-degree rank on odd 1..499.
    for n in sorted(set(range(1,129))|set(range(1,500,2))):
        vs=list(shell(n));assert sum(map(weight,vs))==tau[n]
        stats['shell_sum_checks']+=1
        if n<=128:
            groups=defaultdict(list)
            for v in vs:groups[gcd(*v)].append(v)
            primitive[n]=sum(weight(v) for v in groups.get(1,[]))
            expected=sum(mobius(d)*chi(d)*d**10*tau[n//(d*d)]
                         for d in range(1,isqrt(n)+1) if n%(d*d)==0)
            assert primitive[n]==expected
            stats['primitive_mobius_checks']+=1
            for g,pts in groups.items():
                assert g%5 and n%(g*g)==0
                sums=[0]*len(K)
                for v in pts:
                    u=tuple(v[(g*j)%5]//g for j in range(5))
                    assert gcd(*u)==1 and all(u[j]%5==j for j in range(5))
                    assert sum(u)==0 and sum(x*x for x in u)==10*n//(g*g)
                    assert weight(v)==chi(g)*g**10*weight(u)
                    qs=kernel_values(K,v)
                    for j,x in enumerate(qs):sums[j]+=weight(v)*x
                    stats['content_scaling_packet_checks']+=1
                assert not any(sums)
                stats['content_kernel_zero_checks']+=len(K)
            if n in [4,9,25,49,81]:
                content_examples.append(dict(n=n,tau=tau[n],primitive=primitive[n],
                    contents=[dict(g=g,packets=len(pts),mass=sum(map(weight,pts))) for g,pts in sorted(groups.items())]))
        if n%2:
            keys,mass,M=table(vs,K[:5],1);r=rank(M)
            assert all(sum(row[j] for row in M)==0 for j in range(5))
            stats['coarse_rank_checks']+=1
            if prime(n):coarse_prime_checks+=1
            if r!=len(keys)-1:coarse_fail.append(dict(n=n,sectors=len(keys),rank=r,prime=prime(n)))
    assert [x['n'] for x in coarse_fail]==[9,81]
    profiles=[]
    for n in [31,37,41,59,71,9,49,81]:
        vs=list(shell(n));rows=[]
        for k in [1,2,3]:
            keys,mass,M=table(vs,K,k);stages=[]
            for d in [14,20,22,24,26,28]:
                jjs=[j for j,q in enumerate(K) if q['degree']<=d]
                r=rank([[row[j] for j in jjs] for row in M])
                stages.append(dict(degree=d,rank=r,total_preserving_defect=len(keys)-1-r))
                stats['profile_exact_ranks']+=1
            rows.append(dict(depth=k,sectors=len(keys),stages=stages))
        keys,mass,M=table(vs,K,None)
        contents=[gcd(*v) for v in keys];c=len(set(contents));r=rank(M)
        assert r<=len(keys)-c
        if n in [9,49,81]:assert r==len(keys)-c
        profiles.append(dict(n=n,tree=rows,terminal_orbits=len(keys),
                             content_classes=sorted(set(contents)),terminal_rank=r,
                             content_preserving_defect=len(keys)-c-r))
    # Explicit two-stage transport on p=31, using only degrees <=22.
    L=[q for q in K if q['degree']<=22];vs=list(shell(31))
    kc,sc,Mc=table(vs,L,1);kf,sf,Mf=table(vs,L,2)
    parent=[kc.index(sector(next(v for v in vs if sector(v,4)==key),2)) for key in kf]
    A=[[int(parent[j]==i) for j in range(len(kf))] for i in range(len(kc))]
    assert matmul(A,Mf)==Mc and matvec(A,sf)==sc
    N=transpose(nullspace(Mc));B=matmul(Mf,N)
    assert rank(Mc)==5 and rank(Mf)==15 and rank(B)==10
    assert matmul(A,B)==[[0]*len(B[0]) for _ in A]
    # Kill every coarse sector but the last. No tau value is supplied to the solve.
    ac=solve(Mc[:-1],[-x for x in sc[:-1]])
    after=[a+b for a,b in zip(sf,matvec(Mf,ac))]
    parents=matvec(A,after)
    assert parents[:-1]==[0]*5
    target=[F(0)]*len(kf)
    for i in range(len(kc)):
        anchor=max(j for j,p in enumerate(parent) if p==i)
        target[anchor]=parents[i]
    z=solve(B,[a-b for a,b in zip(target,after)])
    ad=matvec(N,z);final=[a+b for a,b in zip(after,matvec(Mf,ad))]
    assert final==target and matvec(Mc,ad)==[0]*6
    assert len([x for x in final if x])==1 and sum(final)==tau[31]
    # The degree-20 residual is removed by a degree-22 column.
    M20=[row[:14] for row in Mf];dual=nullspace(transpose(M20))
    lam=next(v for v in dual if len(set(v))>1)
    lam=[x-lam[-1] for x in lam]
    den=1
    from math import lcm
    den=lcm(*(x.denominator for x in lam));lam=[int(x*den) for x in lam]
    gg=gcd(*lam);lam=[x//gg for x in lam]
    assert matvec(transpose(M20),lam)==[0]*14
    newpairings=matvec(transpose([row[14:] for row in Mf]),lam)
    assert any(newpairings)
    transfer=dict(n=31,coarse_keys=kc,fine_keys=kf,aggregation=A,
                  coarse_mass=sc,fine_mass=sf,coarse_matrix=Mc,fine_matrix=Mf,
                  coefficient_kernel_basis=N,detail_matrix=B,
                  coarse_coefficients=ac,detail_coefficients=ad,
                  after_coarse=after,after_detail=final,
                  degree20_residual_functional=lam,degree22_pairings=newpairings)
    (out/'p31_transport_certificate.json').write_text(json.dumps(enc(transfer),indent=2)+'\n')
    stats['two_stage_exact_transfer_certificates']=1
    # Prime-power arithmetic checks, including exponents far beyond the shell enumeration.
    pp_examples=[]
    for p in range(2,501):
        if not prime(p):continue
        a=tau[p];T=[1,a]
        for r in range(2,41):T.append(a*T[-1]-p**11*T[-2])
        for r in range(2,41):
            R=T[r]-chi(p)*p**10*T[r-2]
            assert R!=0
            if p!=5:assert R%5==(pow(p,r-1,5)*(p+chi(p)))%5
            if r%2 and p not in [2,5]:
                assert R%a==0 and (R//a)%2==1
                assert valuation(R,2)==valuation(a,2)
                stats['odd_prime_power_unit_checks']+=1
            stats['actual_prime_power_checks']+=1
        if p in [2,3,5,7,19,31]:
            pp_examples.append(dict(p=p,tau_p=a,primitive_square=T[2]-chi(p)*p**10,
                                    primitive_cube_over_tau=T[3]//a-chi(p)*p**10))
    # Synthetic values cover the t=5 branch, high valuations and a=0 without assuming Lehmer.
    for p in [3,7,19,29,59,79]:
        for t in range(9):
            for u in range(-30,31,2):
                if u and u%p==0:continue
                a=p**t*u
                if (a-p-chi(p))%5:continue
                T=[1,a]
                for r in range(2,25):T.append(a*T[-1]-p**11*T[-2])
                for m in range(1,13):
                    R=T[2*m]-chi(p)*p**10*T[2*m-2]
                    assert R!=0
                    if a==0:assert R==(-1)**m*p**(11*m-1)*(p+chi(p))
                    elif t<=4:assert valuation(R,p)==2*m*t
                    elif t>=6:assert valuation(R,p)==11*m-1
                    stats['synthetic_even_prime_power_checks']+=1
                if t==5 and a:stats['synthetic_t5_inputs']+=1
    result=dict(status='PASS',counts=dict(stats),generated_kernel_counts=generated,
                coarse_scan=dict(odd_indices=250,odd_primes=coarse_prime_checks,failures=coarse_fail),
                profiles=profiles,content_examples=content_examples,prime_power_examples=pp_examples,
                non_claims=['Not a proof of Lehmer.','No Lean verification.',
                            'Rank results are confined to the executed indices and degrees.',
                            'Uniform primitive theorems rely on the written proofs, not finite sampling.',
                            'No historical novelty claim.'])
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status='PASS',counts=dict(stats),generated=generated,
                          coarse_scan=result['coarse_scan']),indent=2))


if __name__=='__main__':main(sys.argv[1])
