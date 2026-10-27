#!/usr/bin/env python3
"""Exact arithmetic checks for finite-observation and Witt carry obstructions.

All integer/rational tests are exact. This is NOT a proof of the abc conjecture.
Infinite-family statements must be read with their mathematical arguments.
"""
import json, random
from collections import Counter
from fractions import Fraction as Q
from itertools import product
from math import comb, gcd
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'evidence/results.json'

def primes_through(n):
    return [p for p in range(2,n+1) if all(p%d for d in range(2,int(p**.5)+1))]

def pvaluation(n,p):
    e=0
    while n%p==0 and n:
        n//=p
        e+=1
    return e

def order_mod(a,m):
    if m==1:return 1
    assert gcd(a,m)==1
    v=a%m; e=1
    while v!=1:
        v=v*a%m;e+=1
        assert e<=m, (a,m,e)
    return e

def periodic_certificate(p,q,M,k):
    e=pvaluation(M,p)
    coprime=M//p**e
    L=order_mod(p,coprime)
    assert k>=e
    sampled=[p**(k+L*j) for j in range(3)]
    assert len({x%M for x in sampled})==1, (p,q,M,k,L,sampled)
    U=p**L;V=q**L;B=q**k;A=p**k
    target=[B*V**j for j in range(3)]
    numerator=abs(U*target[0]-(U+1)*target[1]+target[2])
    assert numerator==B*(V-1)*abs(V-U)
    optimum=Q(numerator,2*(U+1))
    signed=Q(U*target[0]-(U+1)*target[1]+target[2],2*(U+1))
    # Equal-sign alternating residual certificate (t,-t,t).
    slope=(Q(target[1]-target[0])+2*signed)/(A*(U-1))
    const=Q(target[0])-signed-slope*A
    residual=[Q(target[j])-slope*A*U**j-const for j in range(3)]
    assert residual==[signed,-signed,signed], (p,q,M,k,residual)
    assert max(abs(x) for x in residual)==optimum
    return {"p":p,"q":q,"M":M,"k":k,"L":L,"modular_state":sampled[0]%M,
      "selected_powers":sampled,"target_values":target,
      "sharp_error":str(optimum),"witness_lambda":str(slope),"witness_kappa":str(const)}

def convolve(a,b):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c

def polyphase_filter(p,s,d):
    U=p**s
    a=[1]
    for _ in range(d+1):a=convolve(a,[-1,1])
    return convolve(a,[-U,1])

def solve_square(a,b):
    """Gaussian elimination over fractions for square nonsingular matrix."""
    n=len(a)
    v=[[Q(x) for x in row]+[Q(y)] for row,y in zip(a,b)]
    for c in range(n):
        piv=next((r for r in range(c,n) if v[r][c]),None)
        assert piv is not None, (a,b,c)
        v[c],v[piv]=v[piv],v[c]
        scale=v[c][c]
        v[c]=[x/scale for x in v[c]]
        for r in range(n):
            if r!=c:
                factor=v[r][c]
                v[r]=[x-factor*y for x,y in zip(v[r],v[c])]
    return [row[-1] for row in v]

def polyphase_certificate(p,q,s,d,k):
    # On shells k,k+s,...,k+(d+2)*s, corrections are lambda*p^depth + P(j).
    assert p<q and p>1
    U=p**s;V=q**s;B=q**k;A=p**k
    filtercoeff=polyphase_filter(p,s,d)
    assert len(filtercoeff)==d+3
    assert sum(abs(z) for z in filtercoeff)==(U+1)*2**(d+1)
    assert sum(filtercoeff[j]*U**j for j in range(d+3))==0
    for power in range(d+1):
        assert sum(filtercoeff[j]*j**power for j in range(d+3))==0
    target=[B*V**j for j in range(d+3)]
    numerator=sum(filtercoeff[j]*target[j] for j in range(d+3))
    assert numerator==B*(V-U)*(V-1)**(d+1)
    signed=Q(numerator,sum(abs(t) for t in filtercoeff))
    # Sign-based equioscillating exact residual, then solve for reconstruction coefficients.
    residual=[signed*(1 if w>0 else -1) for w in filtercoeff]
    matrix=[[A*U**j]+[j**m for m in range(d+1)] for j in range(d+2)]
    coeffs=solve_square(matrix,[target[j]-residual[j] for j in range(d+2)])
    for j in range(d+3):
        reproduced=sum(Q(matrix_row)*co for matrix_row,co in zip([A*U**j]+[j**m for m in range(d+1)],coeffs))
        assert reproduced==Q(target[j])-residual[j]
    assert max(abs(x) for x in residual)==abs(signed)
    return {"p":p,"q":q,"s":s,"d":d,"k":k,"sharp_error":str(abs(signed)),
       "numerator":numerator,"filter_coefficients":filtercoeff,
       "witness_coefficients":[str(x) for x in coeffs]}

def teich(x,p,N):
    return pow(x%p,p**(N-1),p**N)

def carry(p,N,x,y):
    mod=p**N;z=(x+y)%p
    delta=(teich(x,p,N)+teich(y,p,N)-teich(z,p,N))%mod
    assert delta%p==0
    return delta//p

def test_witt(p,N,strict_triples=True):
    mod=p**N;cm=p**(N-1)
    lift=[teich(i,p,N) for i in range(p)]
    assert lift[0]==0 and lift[1]==1
    for x in range(p):
        assert lift[x]%p==x
        for y in range(p):
            assert lift[(x*y)%p] == (lift[x]*lift[y])%mod
            c=carry(p,N,x,y)
            assert lift[(x+y)%p]==(lift[x]+lift[y]-p*c)%mod
    cycle=sum(carry(p,N,1,i) for i in range(p))%cm
    assert cycle==1
    if strict_triples:
        for x,y,z in product(range(p),repeat=3):
            lhs=(carry(p,N,x,y)+carry(p,N,(x+y)%p,z))%cm
            rhs=(carry(p,N,y,z)+carry(p,N,x,(y+z)%p))%cm
            assert lhs==rhs
    # Change section by arbitrary p-adic cochain and see the nonzero residue survive.
    rng=random.Random(p*1009+N)
    for _ in range(4):
        b=[rng.randrange(cm) for _ in range(p)]
        s=[(lift[i]+p*b[i])%mod for i in range(p)]
        def adjusted(x,y):
            delta=(s[x]+s[y]-s[(x+y)%p])%mod
            assert delta%p==0
            return delta//p
        adjusted_cycle=sum(adjusted(1,i) for i in range(p))%cm
        assert adjusted_cycle%p==1, (p,N,adjusted_cycle)
        assert adjusted_cycle==(1+p*b[1])%cm, (p,N,adjusted_cycle,b[1])
    return {"p":p,"N":N,"cycle":cycle,"pairs":p*p,"triples":p**3 if strict_triples else 0}

def main():
    out={"finite_observation":{},"polyphase":{},"witt":{},"boundary_tests":{}}
    periodic=[]
    for p,q in [(2,3),(3,5),(5,7)]:
        for M in [4,8,9,12,15,27,40,45,72,100,360,997]:
            e=pvaluation(M,p)
            for shift in [0,1,5]:
                periodic.append(periodic_certificate(p,q,M,max(1,e)+shift))
    assert len(periodic)==108
    out['finite_observation']={"cases":len(periodic),"sample_certificates":[x for x in periodic if (x['p'],x['q'],x['M'],x['k']) in [(2,3,12,2),(2,3,360,3),(3,5,27,3)]],
      "max_period":max(x['L'] for x in periodic),"pass":True}
    polyphase=[]
    for p,q in [(2,3),(3,5),(5,7)]:
        for s,d,k in product(range(1,6),range(0,7),range(1,5)):
            polyphase.append(polyphase_certificate(p,q,s,d,k))
    assert len(polyphase)==420
    out['polyphase']={"cases":len(polyphase),"sample_certificates":[x for x in polyphase if (x['p'],x['q'],x['s'],x['d'],x['k']) in [(2,3,1,0,1),(2,3,2,1,1),(3,5,2,2,2)]],"pass":True}
    witt=[]
    for p in primes_through(47):
        for N in [2,3,4]:
            witt.append(test_witt(p,N,strict_triples=(p<=13)))
    assert len(witt)==15*3
    out['witt']={"cases":len(witt),"lift_pairs":sum(x['pairs'] for x in witt),"cocycle_triples":sum(x['triples'] for x in witt),"nontrivial_cycle_each":True,"pass":True,
     "sample":[x for x in witt if (x['p'],x['N']) in [(2,2),(3,2),(5,3),(11,4)]]}
    # Explicit no-go: the naive additive section to Z/9 (or any Z/p²) is impossible.
    # A lifted generator 1+p*t has p*(1+p*t)=p mod p², never 0.
    for p in primes_through(47):
        for t in range(p):
            assert (p*(1+p*t))%(p*p)==p
    # Additive identities still hold as positive control in target ring when carry restored.
    for x,y in product(range(3),repeat=2):
        lhs=(teich(x,3,2)+teich(y,3,2))%9
        rhs=(teich((x+y)%3,3,2)+3*carry(3,2,x,y))%9
        assert lhs==rhs
    out['boundary_tests']={"no_additive_split_mod_p_squared":sum(primes_through(47)),
       "explicit_p3_carry_1_plus_1":carry(3,2,1,1),
       "note":"classical nonsplit additive extension; no abc-height claim"}
    RESULT.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({"periodic":len(periodic),"polyphase":len(polyphase),"witt":len(witt),
     "witt_pairs":out['witt']['lift_pairs'],"witt_triples":out['witt']['cocycle_triples'],
     "sample_M12":out['finite_observation']['sample_certificates'][0] if out['finite_observation']['sample_certificates'] else None},indent=2))
    print('PASS',RESULT)
if __name__=='__main__':main()
