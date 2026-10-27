#!/usr/bin/env python3
"""Exact bounded checks for the radix analytic transport and its unit boundary."""
import hashlib
import json
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]

def v2(n):
    if not n:
        return None
    n=abs(n)
    return (n & -n).bit_length()-1

def weight(n,m,c):
    return c*m+v2(comb(n,m))

def pmul(a,b):
    out=[Fraction(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j]+=x*y
    return out

def pscale(a,c):
    return [x*c for x in a]

def binompoly(a,b,m):
    p=[Fraction(1)]
    for i in range(m):
        p=pmul(p,[Fraction(a-i),Fraction(b)])
    return pscale(p,Fraction(1,factorial(m)))

def divpoly(a,b):
    rem=a[:]
    quot=[Fraction(0)]*(len(a)-len(b)+1)
    for j in range(len(quot)-1,-1,-1):
        z=rem[j+len(b)-1]/b[-1]
        quot[j]=z
        for i,t in enumerate(b):
            rem[i+j]-=z*t
    assert not any(rem)
    return quot

def integral_mod2(x):
    assert x.denominator % 2
    return x.numerator % 2

def log9over8(bits):
    mod=1<<bits
    ans=0
    for k in range(1,2*bits+3):
        t=v2(k)
        e=3*(k-1)-t
        if e<bits:
            ans+=(1 if k%2 else -1)*(1<<e)*pow(k>>t,-1,mod)
    return ans%mod

def sourcejet(x,bits):
    n=x+1
    assert n>0
    d=n*(2*n-1)
    t=v2(d)
    p=bits+2*t
    mod=1<<p
    f=((pow(9,n,1<<(p+3))-1)%(1<<(p+3)))>>3
    fp=pow(9,n,mod)*log9over8(p)%mod
    ap=(fp*d-f*(4*x+3))%mod
    assert ap%(1<<(2*t))==0
    der=(ap>>(2*t))*pow((d>>t)**2,-1,1<<bits)%(1<<bits)
    assert f%(1<<t)==0
    val=(f>>t)*pow(d>>t,-1,1<<bits)%(1<<bits)
    return val,der

def sourcechart(bits, degree=8):
    mod=1<<bits
    x0=10202
    n0=x0+1
    ell=8*log9over8(bits+10)
    e=ell*(1<<15)
    f=[((pow(9,n0,1<<(bits+3))-1)%(1<<(bits+3)))>>3]
    for k in range(1,degree+1):
        denominator=8*factorial(k)
        t=v2(denominator)
        numerator=pow(9,n0,1<<(bits+t))*pow(e,k)
        assert numerator%(1<<t)==0
        f.append((numerator>>t)*pow(denominator>>t,-1,mod)%mod)
    d=[n0*(2*x0+1),(1<<15)*(2*x0+1)+(1<<16)*n0,1<<31]
    di=pow(d[0],-1,mod)
    ans=[]
    for k in range(degree+1):
        ans.append((f[k]-sum(d[j]*ans[k-j] for j in range(1,min(k,2)+1)))*di%mod)
    assert all(a%(1<<(15*k))==0 for k,a in enumerate(ans))
    return ans

def evaluate(poly,x,mod):
    value=0
    for a in reversed(poly):
        value=(value*x+a)%mod
    return value

def halfder(poly):
    assert all((i*poly[i])%2==0 for i in range(1,len(poly)))
    return [i*poly[i]//2 for i in range(1,len(poly))]

def main(outpath):
    tests=0
    # Independent integer binomial construction of the first radix weight law.
    for Q in range(1,13):
        for a in range(16):
            N=16*Q+a
            for q in range(Q+1):
                assert weight(N,16*q,4)==weight(Q,q,64)
                tests+=1
            for m in range(N):
                if (m+1)%16:
                    assert weight(N,m+1,4)>weight(N,m,4)
                    tests+=1
    polynomial_tests=0
    for a in range(16):
        for q in range(1,5):
            numerator=binompoly(a,16,16*q)
            denominator=binompoly(0,1,q)
            quotient=divpoly(numerator,denominator)
            assert pmul(denominator,quotient)==numerator
            assert integral_mod2(quotient[0])==1
            assert all(integral_mod2(x)==0 for x in quotient[1:])
            polynomial_tests+=1
    # Complete inherited coefficients only. No new actual-index reconstruction.
    inp=ROOT/'shifted_obstruction/critical_arithmetic/inherited_coefficients.json'
    records=json.loads(inp.read_text())['records']
    rec=next(r for r in records if r['T']=='0')
    coeff=[int(x) for x in rec['jet'][0]]
    assert rec['local_coefficient_bits']==94
    assert [coeff[i]%256 for i in range(3)]==[213,88,81]
    bits=220
    mod=1<<bits
    x=10202
    aa,ad=sourcejet(x,bits)
    av,adv=sourcejet(x-1,bits)
    p=x*(2*x-1)
    pd=4*x-1
    jj=p*av%mod
    jd=(pd*av+p*adv)%mod
    det=(aa*jd-ad*jj)%mod
    assert det%2
    g=(coeff[0]<<178)%mod
    gp=(coeff[1]<<163)%mod
    assert v2(g)==178 and v2(gp)==166
    di=pow(det,-1,mod)
    d0=(-jd*g+jj*gp)*di%mod
    d1=(ad*g-aa*gp)*di%mod
    assert (g+aa*d0+jj*d1)%mod==0
    assert (gp+ad*d0+jd*d1)%mod==0
    assert v2(d0)>=166 and v2(d1)>=166
    assert v2((1<<154)+d0)==154
    # Any odd first-packet unit retains its valuation under this correction.
    for unit in range(1,32,2):
        assert v2((unit<<153)+d1)==153
    # One-coefficient deformation: joint Hensel lift of the complete93-bit model.
    local_bits=93
    lp=sourcechart(local_bits+1)
    independent_value,independent_derivative=sourcejet(10202,local_bits+1)
    assert lp[0]==independent_value
    assert lp[1]==(independent_derivative<<15)%(1<<(local_bits+1))
    kh=halfder(coeff)
    lh=halfder(lp)
    assert [a%2 for a in kh[:2]]==[0,1]
    assert all(a%2==0 for a in kh[2:])
    assert all(a%(1<<15)==0 for a in lh)
    center,parameter=0,0
    for k in range(local_bits):
        md=1<<(k+1)
        solutions=[]
        for z in [center,center+(1<<k)]:
            for u in [parameter,parameter+(1<<k)]:
                if (evaluate(coeff,z,md)+u*evaluate(lp,z,md))%md==0 and (evaluate(kh,z,md)+u*evaluate(lh,z,md))%md==0:
                    solutions.append((z,u))
        assert len(solutions)==1
        center,parameter=solutions[0]
    assert parameter%2==1
    assert center%2==0
    # Exact linearized curvature is odd after division by2.
    curvature=[(i+1)*kh[i+1] for i in range(len(kh)-1)]
    curvature_l=[(i+1)*lh[i+1] for i in range(len(lh)-1)]
    assert (evaluate(curvature,center,2)+parameter*evaluate(curvature_l,center,2))%2==1
    result={
      'claim':'Exact radix unit lift and unit-preserving local double-contact boundary',
      'domain':'exact integers, Fractions, and Z/2^220Z; no floating point',
      'weight_checks':tests,
      'polynomial_quotient_checks':polynomial_tests,
      'weight_bounds':{'Q':[1,12],'a':[0,15],'q':[0,'Q'],'C':4,'B':16},
      'polynomial_bounds':{'a':[0,15],'q':[1,4],'B':16},
      'jet_input_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),
      'source_jet':{'x':x,'bits':bits,'determinant_odd':True},
      'target_jet_valuations':[v2(g),v2(gp)],
      'correction_valuations':[v2(d0),v2(d1)],
      'correction_residues':[str(d0),str(d1)],
      'corrected_value_and_derivative_residues':[0,0],
      'individual_original_coefficient_valuations_preserved':[154,153],
      'interpretation':'The proof gives exact dyadic double contact by a unit two-jet matrix. This modular check supports that construction and is not an actual singular Euler index.',
      'one_coefficient_model':{'bits':local_bits,'center_residue':str(center),'parameter_residue':str(parameter),'parameter_odd':True,'stationary_value_residue':0,'half_derivative_residue':0,'curvature_divided_by_two_odd':True,'relative_kernel_change_valuation':24,'scope':'A dyadic coefficient deformation, not an actual Euler index.'},
      'all_checks_passed':True,
    }
    Path(outpath).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['weight_checks','polynomial_quotient_checks','target_jet_valuations','correction_valuations','all_checks_passed']}))

if __name__=='__main__':
    main(sys.argv[1])
