#!/usr/bin/env python3
"""Exact finite checks of the prescribed Bernoulli norm theorem."""
from fractions import Fraction as F
from math import comb, factorial
from pathlib import Path
import json, sys

def add(a,b):
    return [(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)
            for i in range(max(len(a),len(b)))]
def scale(a,t):return [t*x for x in a]
def mul(a,b):
    c=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c
def residue(x,mod=8):
    x=F(x)
    assert x.denominator%2
    return x.numerator*pow(x.denominator,-1,mod)%mod
def bn(n):return -F((2*n)**4,16*n*n-1)-F((2*n+1)**4,4*(2*n+1)**2-1)
def an(n):return F((2*n)**4*(2*n-1)**4,(4*n-3)*(4*n-1)**2*(4*n+1))

def main(out):
    B=[F(1)]
    for n in range(1,65):B.append(-sum(F(comb(n+1,k))*B[k] for k in range(n))/F(n+1))
    D=[F(1)]+[(2-4**n)*B[2*n] for n in range(1,33)]
    P=[[F(1)]]
    for n in range(4):
        pn=add([F(0)]+P[n],scale(P[n],-bn(n)))
        if n:pn=add(pn,scale(P[n-1],-an(n)))
        P.append(pn)
    E=[scale(P[n],F(1,4**n*factorial(n)**2)) for n in range(5)]
    def gram(x,actual,m):
        moments=[2*B[2*(x+k)] if actual else D[x+k] for k in range(2*m-1)]
        return [[sum(a*moments[k] for k,a in enumerate(mul(E[i],E[j])))
                 for j in range(m)] for i in range(m)]
    def quad(M,v):return sum(M[i][j]*v[i]*v[j] for i in range(len(v)) for j in range(len(v)))
    congruences=0;patterns=0
    for actual,xx in [(False,range(13)),(True,range(10,25))]:
        for x in xx:
            M=gram(x,actual,4)
            for i in range(4):
                for j in range(4):
                    if i==j:assert residue(M[i][j])==(1+4*x)*5**i%8
                    else:assert residue(M[i][j],4)==0
                    congruences+=1
            for k in range(256):
                v=[(k//4**i)%4 for i in range(4)]
                if not any(t%2 for t in v):continue
                assert residue(quad(M,v))!=0
                patterns+=1
    isotropic=[];bits=40;mod=1<<bits
    for actual,x in [(False,0),(False,7),(True,16),(True,23)]:
        M=gram(x,actual,5);w=[1,0,1,1,2]
        A=M[1][1];b=sum(M[1][i]*w[i] for i in range(5));C=quad(M,w)
        d=(b/A)**2-C/A
        assert residue(d)==1
        dd=residue(d,mod);t=1
        for n in range(3,bits):
            if (t*t-dd)%(1<<(n+1)):t+=1<<(n-1)
            assert (t*t-dd)%(1<<(n+1))==0
        y=(t-residue(b/A,mod))%mod
        v=w.copy();v[1]=y
        assert residue(quad(M,v),mod)==0
        isotropic.append({'actual_Bernoulli':actual,'shift':x,'bits':bits,'basis_coordinates':v,'norm_residue':0,'interpretation':'The exact isotropic vector is supplied by the square-root proof; this is its finite lift.'})
    result={'status':'passed','depleted_shifts':[0,12],'actual_shifts':[10,24],
            'gram_congruence_checks':congruences,'primitive_mod4_vectors_checked':patterns,
            'isotropic_lifts':isotropic,'nonclaims':['No representation of the Euler stationary scalar as this norm','No Euler simplicity conclusion','Finite checks do not prove the universal quantifiers without the accompanying argument']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'passed','gram_checks':congruences,'primitive_vectors':patterns,'isotropic_lifts':len(isotropic)}))
if __name__=='__main__':main(sys.argv[1])
