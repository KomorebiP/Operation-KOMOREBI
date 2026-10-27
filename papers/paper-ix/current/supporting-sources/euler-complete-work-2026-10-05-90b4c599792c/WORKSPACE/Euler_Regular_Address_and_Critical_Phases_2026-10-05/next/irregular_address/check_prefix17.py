#!/usr/bin/env python3
"""Exact finite prefix certificate, plus bounded independent checks.

Standard library only. Transfer to every actual Euler wall uses the explicit
congruence/loss proof in irregular_address17.md, not model-depth sampling.
"""
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import hashlib, json, platform, sys, time


def v2(n):
    if not n:
        raise ValueError('v2(0) not used')
    n=abs(n)
    return (n&-n).bit_length()-1


def modf(x, modulus=64):
    x=F(x)
    assert x.denominator%2
    return x.numerator*pow(x.denominator,-1,modulus)%modulus


def bernoulli(n):
    out=[F(1)]
    for m in range(1,n+1):
        out.append(-sum((F(comb(m+1,k))*out[k] for k in range(m)),F(0))/(m+1))
    return out


def choose_integer(n,k):
    out=1
    for h in range(k):
        out*=n-h
    assert out%factorial(k)==0
    return out//factorial(k)


def bernoulli_residue_polynomial(n, B):
    # Finite polynomial only: not a Bernoulli number of negative index.
    return sum(choose_integer(n,h)*modf((1<<h)*B[h]) for h in range(7))%64


def prefix_coefficient_model(r,q,B):
    # Algebraic finite-congruence model. Only q=0,1,2 are needed modulo64.
    if q==0:
        return 1
    den=1;denvaluation=0
    for h in range(1,2*q+1):
        z=2*r+h
        vv=v2(z)
        denvaluation+=vv
        den=den*(z//(1<<vv))%64
    cost=5*q-denvaluation
    assert cost>=0
    unit=(2*r+2*q-1)*pow(2*r-1,-1,64)%64
    unit=unit*bernoulli_residue_polynomial(2*r+2*q,B)%64
    unit=unit*pow(bernoulli_residue_polynomial(2*r,B),-1,64)%64
    unit=unit*pow(den,-1,64)%64
    return ((1<<cost)*unit)%64


def trim(p):
    while len(p)>1 and p[-1]==0:
        p.pop()
    return p


def add(p,q):
    out=[0]*max(len(p),len(q))
    for i,x in enumerate(p):out[i]+=x
    for i,x in enumerate(q):out[i]+=x
    return trim([x%64 for x in out])


def mul(p,q):
    out=[0]*(len(p)+len(q)-1)
    for i,x in enumerate(p):
        for j,y in enumerate(q):out[i+j]+=x*y
    return trim([x%64 for x in out])


def affine(p,a):
    out=[0]
    for x in reversed(p):
        out=mul(out,[a,1]);out[0]=(out[0]+x)%64
    return trim(out)


def evaluate(p,x):
    z=0
    for a in reversed(p):z=(z*x+a)%64
    return z


def source_coefficients():
    log8=0
    for h in range(1,9):
        cost=3*h-3-v2(h)
        if cost<6:
            term=(1<<cost)*pow(h//(1<<v2(h)),-1,64)
            log8=(log8+(-term if h%2==0 else term))%64
    numerator=[0]
    for h in range(7):
        f=factorial(h+1);cost=3*h-v2(f)
        if cost>=6:continue
        coef=(1<<cost)*pow(log8,h+1,64)*pow(f//(1<<v2(f)),-1,64)%64
        numerator=add(numerator,[coef*comb(h,j)%64 for j in range(h+1)])
    out=mul(numerator,[pow(-2,h,64) for h in range(6)])
    return log8,out


def run():
    start=time.monotonic();B=bernoulli(34)
    residues=[bernoulli_residue_polynomial(-34+2*q,B) for q in range(3)]
    assert residues==[13,1,21]
    for q in range(3):
        assert residues[q]==modf(2*B[30+2*q])
    coeffs=[prefix_coefficient_model(-17,q,B) for q in range(3)]
    assert coeffs==[1,55,16]
    # Congruent ordinary positive depths provide an additional implementation
    # comparison; uniformity is proved in the accompanying note.
    for exponent in (20,32,64,128):
        for multiplier in (1,3,7):
            r=multiplier*(1<<exponent)-17
            assert [prefix_coefficient_model(r,q,B) for q in range(3)]==coeffs
    log8,A=source_coefficients()
    assert log8==61
    assert A==[1,34,28,8,48,32]
    for x in range(64):
        exact=F(9**(x+1)-1,8*(x+1)*(2*x+1))
        assert evaluate(A,x)==modf(exact)
    P0=[1];P1=mul([0,1],[-1,2]);P2=mul(mul(P1,[-1,1]),[-3,2])
    S=[0]
    for q,p in enumerate((P0,P1,P2)):
        S=add(S,[(coeffs[q]*z)%64 for z in mul(p,affine(A,-q))])
    assert S==[1,13,40,8,48,32]
    derivative=[i*S[i]%64 for i in range(1,len(S))]
    roots=[x for x in range(64) if evaluate(S,x)==0]
    assert roots==[43]
    assert all(evaluate(derivative,x)%2==1 for x in range(64))
    assert evaluate(S,11)==32 and v2(43-11)==5
    costs=[3*q+(16).bit_count()-(16-q).bit_count() for q in range(17)]
    assert costs==[0,0,4,7,11,13,17,20,24,25,29,32,36,38,42,45,49]
    assert min(costs[3:])==7
    g=[(ell-ell.bit_count())+(16-ell-(16-ell).bit_count()) for ell in range(17)]
    h=[max(ell,16-ell).bit_length() for ell in range(17)]
    assert min(g)==11 and max(h)==5 and g[11]==11 and h[11]==4
    k=1<<53
    assert (3*k+54)+(k-54+16)==4*k+16
    return {"status":"PASS","arithmetic":"exact integers and rational fractions; modulo64",
            "bernoulli_residues":[13,1,21],"prefix_coefficients_q0_q1_q2":coeffs,
            "source_coefficients_mod64":A,"prefix_coefficients_mod64":S,
            "prefix_root_mod64":43,"root_displacement_from_11":5,
            "packet_valuations":costs,"lower_skeleton_derivative_valuations":g,
            "lower_skeleton_scales":h,
            "critical_first_complement":{"k":k,"outer_L":4*k+16,"delta":k-38},
            "checks":{"exact_small_Bernoulli_comparisons":3,"congruent_positive_model_depths":12,
                      "exact_rational_source_values":64,"derivative_unit_residues":64,
                      "root_residues_mod64":64},
            "scope":"Coefficientwise six-bit prefix certificate. Uniform transfer to actual enormous Euler depths is established separately by the explicit precision-loss proof. No tangency exclusion at the surviving critical scale.",
            "python":sys.version,"platform":platform.platform(),
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "elapsed_seconds":time.monotonic()-start}

if __name__=='__main__':
    result=run()
    out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).with_name('PREFIX17_CERTIFICATE.json')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({"status":result['status'],"sigma_mod64":result['prefix_root_mod64'],
                      "critical_first_complement":result['critical_first_complement'],
                      "output":str(out)},indent=2))
