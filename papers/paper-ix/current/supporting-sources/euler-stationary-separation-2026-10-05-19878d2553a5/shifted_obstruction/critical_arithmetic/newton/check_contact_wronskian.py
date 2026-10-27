#!/usr/bin/env python3
"""Independent small exact/modular checks of the contact identities.

The general theorems have proofs in PREFIX_CONTACT_AND_WRONSKIAN.md.
No actual large-r parameter digits are computed.
"""
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import json
import sys

BITS=32
MOD=1<<BITS


def v2(x):
    x %= MOD
    return (x & -x).bit_length()-1 if x else BITS


def fm(x):
    x=F(x)
    assert x.denominator % 2
    return x.numerator*pow(x.denominator,-1,MOD)%MOD


def trim(a):
    while len(a)>1 and a[-1]==0:a.pop()
    return a


def add(a,b,sign=1):
    return trim([((a[i] if i<len(a) else 0)+sign*(b[i] if i<len(b) else 0))%MOD
                 for i in range(max(len(a),len(b)))])


def scale(a,c):return trim([c*x%MOD for x in a])


def mul(a,b):
    z=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):z[i+j]=(z[i+j]+x*y)%MOD
    return trim(z)


def der(a):return trim([i*a[i]%MOD for i in range(1,len(a))] or [0])


def shift(a,c):
    z=[0]*len(a)
    for i,x in enumerate(a):
        for j in range(i+1):z[j]=(z[j]+x*comb(i,j)*pow(c,i-j,MOD))%MOD
    return trim(z)


def ev(a,c):
    z=0
    for x in reversed(a):z=(z*c+x)%MOD
    return z


def bernoulli(n):
    b=[F(1)]
    for m in range(1,n+1):
        b.append(-sum(F(comb(m+1,k))*b[k] for k in range(m))/(m+1))
    return b


def main(out):
    # A=(sum 8^n fall_n/(n+1)!)/(1+2s). Complete coefficient error >=2^32.
    numerator=[0];fall=[1]
    for n in range(18):
        numerator=add(numerator,scale(fall,fm(F(8**n,factorial(n+1)))))
        fall=mul(fall,[-n,1])
    A=mul(numerator,[pow(-2,j,MOD) for j in range(BITS)])
    L=sum(((-1)**(k+1))*F(8**k,k) for k in range(1,BITS+1))
    X=trim([fm(L**n/factorial(n)) for n in range(BITS+1)])
    U=add([1],scale(X,3))
    J=trim([0]+[fm(L**n/F(8*factorial(n))) for n in range(1,BITS+1)])
    determinant=add(mul(A,der(J)),mul(der(A),J),-1)
    assert determinant[0]%2==1 and all(x%2==0 for x in determinant[1:])
    maxm=11
    b=bernoulli(2*maxm)
    beta=[F(1)]+[-F(2**(2*m)*(2*m-1),factorial(2*m))*b[2*m]
                    for m in range(1,maxm+1)]
    P=[[1]]
    for m in range(maxm):P.append(mul(P[-1],mul([-m,1],[-2*m-1,2])))
    packets=[mul(P[m],shift(A,-m)) for m in range(maxm+1)]
    prefixes=[[0]]
    for m in range(maxm+1):
        prefixes.append(add(prefixes[-1],scale(packets[m],fm(8**m*beta[m]))))
    E=prefixes[-1]
    full=mul(U,E)
    derivative_checks=0
    contact_checks=0
    records=[]
    for r in range(1,8):
        S=prefixes[r]
        Ftail=add(E,S,-1)
        assert min(v2(x) for x in Ftail)>=3*r
        C=mul(U,S);B=add(full,C,-1)
        assert min(v2(x) for x in B)>=3*r+2
        dC=C
        for j in range(r):
            for a in range(8):
                assert v2(ev(dC,a))==3*j+2
                derivative_checks+=1
            dC=der(dC)
        W=add(mul(full,der(C)),mul(der(full),C),-1)
        right=mul(mul(U,U),add(mul(E,der(S)),mul(der(E),S),-1))
        assert W==right
        assert W==add(mul(der(full),B),mul(full,der(B)),-1)
        assert min(v2(x) for x in W)>=min(BITS,3*r+4)
        # Hbar_r is the exact factored tail modulo the working precision.
        H=[0]
        for q in range(maxm-r+1):
            H=add(H,scale(packets[q],fm(8**(r+q)*beta[r+q])))
        assert mul(P[r],shift(H,-r))==Ftail
        if r<=6:
            for a in range(8):
                va,wa=ev(H,a),ev(der(H),a)
                aa,ja=ev(A,a),ev(J,a)
                ap,jp=ev(der(A),a),ev(der(J),a)
                inv=pow((aa*jp-ap*ja)%MOD,-1,MOD)
                d0=(va*jp-wa*ja)*inv%MOD
                d1=(aa*wa-ap*va)*inv%MOD
                assert v2(d0)>=3*r and v2(d1)>=3*r
                Q=add(add(H,scale(A,d0),-1),scale(J,d1),-1)
                assert ev(Q,a)==0 and ev(der(Q),a)==0
                # J=P1*A(.-1), verified coefficientwise at the same precision.
                assert J==packets[1]
                Stilde=add(add(S,scale(packets[r],d0)),scale(packets[r+1],d1))
                assert add(E,Stilde,-1)==mul(P[r],shift(Q,-r))
                records.append({'r':r,'a':a,'d0':str(d0),'d1':str(d1),
                    'd0_valuation_or_bound':v2(d0),'d1_valuation_or_bound':v2(d1)})
                contact_checks+=1
    result={'status':'passed','precision_bits':BITS,
        'arithmetic':'exact fractions for source constants, then exact integer modular polynomials',
        'actual_prefix_r_range':[1,7],'point_range':[0,7],
        'actual_prefix_derivative_checks':derivative_checks,
        'wronskian_coefficient_identities':14,
        'appended_two_packet_contacts':contact_checks,
        'source_jet_determinant_coefficientwise_unit':True,
        'records':records,
        'nonclaims':['No actual large-r nonvanishing theorem.',
            'Free packet coefficients are dyadic, not asserted Bernoulli or rational.',
            'Finite contact congruences corroborate the exact proof, not exact zeros by themselves.',
            'No parameter digit extension.']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))


if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'CONTACT_CHECKS.json')
