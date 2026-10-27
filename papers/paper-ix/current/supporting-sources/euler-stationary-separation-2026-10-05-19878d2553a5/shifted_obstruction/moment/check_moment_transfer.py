#!/usr/bin/env python3
"""Exact tests of the shifted Bernoulli dictionary and failed norm transfer."""
from fractions import Fraction as F
from math import comb,factorial
from pathlib import Path
import json
import sys

def bernoullis(n):
    b=[F(1)]
    for m in range(1,n+1):
        b.append(-sum(F(comb(m+1,k))*b[k] for k in range(m))/(m+1))
    return b

def eulers(n):
    e=[1]
    for m in range(1,n+1):e.append(-sum(comb(2*m,2*k)*e[k] for k in range(m)))
    return e

def skeleton(s,n):
    q=F(1)
    for k in range(n):q*=(s-k)*(2*s-2*k-1)
    return q

def A(n):return F(9**(n+1)-1,8*(n+1)*(2*n+1))

def v2(x):
    x=F(x)
    if not x:return None
    a,b=abs(x.numerator),x.denominator
    return (a&-a).bit_length()-(b&-b).bit_length()

def main(out):
    B=bernoullis(82);E=eulers(40)
    beta=[F(1)]+[-F(4**n*(2*n-1),factorial(2*n))*B[2*n] for n in range(1,41)]
    aa=[F(1)]+[F(4**n,factorial(2*n))*B[2*n] for n in range(1,41)]
    counts={'full_reflection':0,'cutoff_reflection':0,'shifted_dictionary':0,
            'forced_defect_zeros':0,'regularized_euler_bound':0}
    for s in range(31):
        nu=2*s+1
        j4=sum(F(comb(nu,k))*4**k*B[k] for k in range(nu+1))
        j43=sum(F(comb(nu,k))*F(4,3)**k*B[k] for k in range(nu+1))
        assert j43==-F(j4,3*9**s)
        counts['full_reflection']+=1
        for r in range(1,min(s+2,20)):
            p4=1-2*nu+sum(16**n*B[2*n]*comb(nu,2*n)
                          for n in range(1,min(r,s+1)))
            p43=1-F(2*nu,3)+sum(F(16,9)**n*B[2*n]*comb(nu,2*n)
                               for n in range(1,min(r,s+1)))
            r4=j4-p4;r43=j43-p43
            assert r43==-F(r4,3*9**s)-p43-F(p4,3*9**s)
            counts['cutoff_reflection']+=1
            if s<r:
                assert 3*9**s*p43+p4==0
                counts['forced_defect_zeros']+=1
            if s:
                u=sum(8**n*aa[n]*F(1,9**n)*skeleton(F(2*s-1,2),n-1)
                      for n in range(r,s+1))
                assert u==F(r43,s*(2*s+1))
                counts['shifted_dictionary']+=1
    reg=[(1+3*9**n)*E[n] for n in range(41)]
    for k in range(41):
        d=sum((-1)**(k-j)*comb(k,j)*reg[j] for j in range(k+1))
        assert v2(d)>=3*k+1
        counts['regularized_euler_bound']+=1
    failures=[]
    for r,k in [(1,6),(2,6),(3,10),(5,14),(9,22),(17,38)]:
        tail=[]
        for n in range(k+1):
            prefix=sum(8**m*beta[m]*skeleton(n,m)*A(n-m)
                       for m in range(min(r,n+1)))
            tail.append((1+3*9**n)*(E[n]-prefix))
        delta=sum((-1)**(k-j)*comb(k,j)*tail[j] for j in range(k+1))
        actual=v2(delta)
        assert actual==3*k and actual<3*k+1
        failures.append({'r':r,'k':k,'actual_v2':actual,'failed_lower_bound':3*k+1,
                         'exact_delta':str(delta)})
    # At a primitive eighth root: cosh9=c, cosh3=-c, cosh1=c.
    # The coefficient of c in the n=0 regularized-source numerator is -4/3.
    pole_numerator=F(-1)-1+F(1-(-1),3)
    assert pole_numerator==F(-4,3)
    # Concrete D(s) filter: rational Amice construction, independently checked
    # against ordinary Euler moments via signed falling-factorial coefficients.
    numerator=[4,8,6,2];denominator=[1,2,5,4,1]
    rat=[]
    for n in range(259):
        rat.append((numerator[n] if n<len(numerator) else 0)
                   -sum(denominator[j]*rat[n-j]
                        for j in range(1,min(n,len(denominator)-1)+1)))
    def L(pol):return [(n+1)*pol[n+1]+n*pol[n] for n in range(len(pol)-1)]
    lr=L(rat);llr=L(lr)
    assert lr[0]==0 and llr[0]==-28
    log=[F(0)]+[F((-1)**(n+1),n) for n in range(1,257)]
    log2=[F(0),F(0)];harmonic=F(1)
    for n in range(2,257):
        if n>2:harmonic+=F(1,n-1)
        log2.append(F(2*(-1)**n,n)*harmonic)
    def filtered_coefficient(n):
        return (rat[n]+2*sum(log[j]*lr[n-j] for j in range(1,n+1))
                +F(1,2)*sum(log2[j]*llr[n-j] for j in range(2,n+1)))
    filtered_powers=[]
    for k in range(2,9):
        actual=v2(filtered_coefficient(2**k))
        assert actual==3-2*k
        filtered_powers.append({'k':k,'degree':2**k,'v2':actual})
    falling=[1]
    for n in range(33):
        moment_check=sum(F(c)*((j//2+1)*(j+1))*(1+3*9**(j//2))*E[j//2]
                         for j,c in enumerate(falling) if j%2==0)/factorial(n)
        assert moment_check==filtered_coefficient(n)
        new=[0]*(len(falling)+1)
        for j,c in enumerate(falling):new[j]-=n*c;new[j+1]+=c
        falling=new
    result={'status':'passed','base_checkpoint':'Euler-arithmetic-nonvanishing-20261005',
            'base_archive_sha256':'15e1f9114380e180adcf4f7306d894100d6fd499929ee7a841d8629bd27e7464',
            'arithmetic':'exact integers and fractions.Fraction','counts':counts,
            'torsion_source_numerator_coefficient':str(pole_numerator),
            'polynomial_filter_power_coefficients':filtered_powers,
            'polynomial_filter_independent_moment_checks':33,
            'strict_bound_counterexamples':failures,
            'nonclaims':['No universal simplicity proof','No critical-value nonvanishing',
                         'Finite strict-bound failures are not Euler counterexamples',
                         'No finite computation verifies an all-precision exponent derivative']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='strict_bound_counterexamples'},indent=2))

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'MOMENT_TRANSFER_CHECKS.json')
