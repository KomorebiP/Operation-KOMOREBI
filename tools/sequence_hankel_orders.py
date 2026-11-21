"""Exact normalized interior recurrence orders; Theorem N, characteristic zero.

This implementation accepts rational t,q. Negative q represents the quadratic
extension needed for v/u=sqrt(q). The theorem itself applies to every
characteristic-zero field. Polynomial coefficient lists are ascending unless
explicitly named descending.
"""
import argparse,json
from fractions import Fraction as F
from math import comb
from pathlib import Path

def trim(poly):
    out=list(poly)
    while out and not out[-1]:out.pop()
    return out

def derivative(poly):return trim([i*poly[i] for i in range(1,len(poly))])

def divide(a,b):
    a,b=trim(a),trim(b)
    if not b:raise ZeroDivisionError('Zero polynomial')
    quotient=[F(0)]*max(0,len(a)-len(b)+1)
    while a and len(a)>=len(b):
        shift=len(a)-len(b);value=a[-1]/b[-1];quotient[shift]=value
        for j,c in enumerate(b):a[shift+j]-=value*c
        a=trim(a)
    return trim(quotient),a

def gcd(a,b):
    a,b=trim(a),trim(b)
    while b:a,b=b,divide(a,b)[1]
    return [c/a[-1] for c in a] if a else []

def characteristic(t,q,coefficients):
    t,q=F(t),F(q)
    first=[sum(F(c)*t**i*q**j for i,j,c in row) for row in coefficients]
    if len(first)!=9 or first[0]!=1:raise ValueError('Expected nine reciprocal characteristic coefficients')
    return first+list(reversed(first[:-1]))

def classify(t,q,coefficients):
    t,q=F(t),F(q)
    if not t or not q:raise ValueError('The interior requires t and q nonzero; use Theorem M on the boundary')
    c=characteristic(t,q,coefficients);f=list(reversed(c))
    h=16-(len(gcd(f,derivative(f)))-1)
    H=[16-8*t,q*(6*t-4),q*(2*t-8),q*q,q*q]
    G=gcd(H,derivative(H));g=len(G)-1
    delta=not (q*q+(36*t*t-16*t+32)*q+64*(t-2)**2)
    if g==0:root_type='1+1+1+1';order=7*h-int(delta)
    elif g==1:root_type='2+1+1';order=7*h+4-int(delta)
    elif g==2 and len(gcd(G,derivative(G)))==1:
        root_type='2+2';order=69
        assert h==9 and not delta
    elif g==2:
        root_type='3+1';order=64
        assert h==8 and not delta
    else:raise ArithmeticError('A quadruple root contradicts the nonzero-family identities')
    return {'t':str(t),'q':str(q),'order':order,'root_type':root_type,
        'distinct_bases':h,'negative_full_collision':bool(delta),'root_gcd_degree':g,
        'recurrence_starts_at':1,'review':'project self-review; see the proof and audit'}

def normalized_terms(t,q,count=8):
    """Defining determinants over Q without choosing sqrt(q)."""
    t,q=F(t),F(q)
    if not q:raise ValueError('The rational basis change requires q nonzero')
    if not 0<=count<=113:raise ValueError('Choose between zero and 113 terms')
    def moment(k):
        m=k//2;value=(1+t*m)*comb(2*m,m)/q**m
        return value if not k%2 else (2*m+1)*value
    out=[]
    for N in range(count):
        M=[[moment(i+j) for j in range(N)] for i in range(N)]
        sign=1;previous=F(1);singular=False
        for k in range(N-1):
            row=next((i for i in range(k,N) if M[i][k]),None)
            if row is None:singular=True;break
            if row!=k:M[row],M[k]=M[k],M[row];sign=-sign
            pivot=M[k][k]
            for i in range(k+1,N):
                for j in range(k+1,N):M[i][j]=(pivot*M[i][j]-M[i][k]*M[k][j])/previous
            for i in range(k+1,N):M[i][k]=F(0)
            previous=pivot
        determinant=F(0) if singular else sign*M[-1][-1] if N else F(1)
        out.append(q**(N*(N-1)//2)*determinant)
    return out

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--coefficients',required=True)
    p.add_argument('--t',required=True);p.add_argument('--q',required=True);a=p.parse_args()
    data=json.loads(Path(a.coefficients).read_text(encoding='utf-8'))
    print(json.dumps(classify(a.t,a.q,data['first_eight_with_unit'])))

if __name__=='__main__':main()
