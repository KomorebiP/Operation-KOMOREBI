#!/usr/bin/env python3
"""Exact finite checks; no claim of universal formal verification.
Boolean functions are integer truth tables, bit x is the value at x.
NOT/CNOT/Toffoli use distinct wires. All controls are positive.
"""
from __future__ import annotations
from pathlib import Path
from itertools import combinations
import argparse, json, random


def one(n): return (1 << (1 << n))-1

def variables(n):
    return [sum(((x>>i)&1)<<x for x in range(1<<n)) for i in range(n)]

def degree(f,n):
    a=[(f>>x)&1 for x in range(1<<n)]
    for i in range(n):
        for x in range(1<<n):
            if x&(1<<i): a[x]^=a[x^(1<<i)]
    return max((x.bit_count() for x,v in enumerate(a) if v),default=-1)

def monomials(n):
    return [sum((x&s==s)<<x for x in range(1<<n)) for s in range(1<<n)]

def immunity(f,n):
    """Return minimum degree of a nonzero h supported in f, and a witness."""
    if not f: return None,0
    neg=one(n)^f; mons=monomials(n)
    for d in range(n+1):
        eligible=[s for s in range(1<<n) if s.bit_count()<=d]
        basis={}
        for j,s in enumerate(eligible):
            col=mons[s]&neg; coeff=1<<j
            while col:
                p=col.bit_length()-1
                if p not in basis:
                    basis[p]=(col,coeff); break
                b,w=basis[p]; col^=b; coeff^=w
            if col==0:
                h=0
                for k,t in enumerate(eligible):
                    if coeff>>k&1: h^=mons[t]
                assert h and not (h&neg) and degree(h,n)==d
                return d,h
    raise AssertionError('point indicator must supply a witness')

def validate(ops,width):
    for g in ops:
        assert g[0] in ('N','C','T')
        assert len(g)=={'N':2,'C':3,'T':4}[g[0]]
        assert len(set(g[1:]))==len(g)-1
        assert all(0<=i<width for i in g[1:])

def step(g,v,mask):
    w=v.copy()
    if g[0]=='N': w[g[1]]^=mask
    elif g[0]=='C': w[g[2]]^=v[g[1]]
    else: w[g[3]]^=v[g[1]]&v[g[2]]
    return w

def trace(ops,v,mask):
    ans=[v.copy()]
    for g in ops: ans.append(step(g,ans[-1],mask))
    return ans

def dnf(n,f):
    gs=[]
    def gate(typ,a,b=None):
        gs.append((typ,a) if b is None else (typ,a,b))
        return n+len(gs)-1
    neg=[gate('NOT',i) for i in range(n)]
    terms=[]
    for x in range(1<<n):
        if not(f>>x&1): continue
        ls=[i if x>>i&1 else neg[i] for i in range(n)]
        t=ls[0]
        for a in ls[1:]: t=gate('AND',t,a)
        terms.append(t)
    if not terms: out=gate('AND',0,neg[0])
    else:
        out=terms[0]
        for t in terms[1:]:out=gate('OR',out,t)
    return gs,out

def compile_source(n,gs,out):
    ops=[]
    for j,g in enumerate(gs):
        t=n+j
        if g[0]=='NOT': ops.extend([('N',t),('C',g[1],t)])
        elif g[1]==g[2]:ops.append(('C',g[1],t))
        elif g[0]=='AND':ops.append(('T',g[1],g[2],t))
        else:ops.extend([('C',g[1],t),('C',g[2],t),('T',g[1],g[2],t)])
    y=n+len(gs); ans=ops+[('C',out,y)]+ops[::-1]
    validate(ans,y+1)
    return ans,y+1,y

def monomial_oracle(n):
    if n==2:return [('T',0,1,n)],n+1,n
    anc=list(range(n,2*n-2)); y=2*n-2
    p=[('T',0,1,anc[0])]
    for i in range(2,n-1):p.append(('T',anc[i-2],i,anc[i-1]))
    ops=p+[('T',anc[-1],n-1,y)]+p[::-1]
    return ops,y+1,y

def check_circuit(n,ops,width,y,f,alpha,full_degrees=True):
    validate(ops,width); mask=one(n)
    z=variables(n)+[0]*(width-n); z[y]=0
    o=z.copy();o[y]=mask
    az=trace(ops,z,mask);ao=trace(ops,o,mask)
    rz=trace(ops[::-1],z,mask);ro=trace(ops[::-1],o,mask)
    end=z.copy();end[y]=f
    assert az[-1]==end
    end[y]^=mask; assert ao[-1]==end
    tc=[0]
    for g in ops:tc.append(tc[-1]+(g[0]=='T'))
    T=tc[-1]; count=0; covector_checks=0
    lam=[0]*width;lam[y]=mask
    cached={}
    def deg(h):
        if h not in cached: cached[h]=degree(h,n)
        return cached[h]
    for j in range(len(ops)+1):
        A=az[j];B=rz[len(ops)-j]
        D=[u^v for u,v in zip(A,ao[j])]
        E=[u^v for u,v in zip(B,ro[len(ops)-j])]
        assert D==E
        H=[u^v for u,v in zip(A,B)]
        union=0; normalizer=0
        for h,d,l in zip(H,D,lam):
            assert h==(f&d)
            union|=h;normalizer^=l&d
        assert union==f and normalizer==mask
        # The covector simultaneously reconstructs the comparison.
        rebuilt=0
        for h,l in zip(H,lam):rebuilt^=h&l
        assert rebuilt==f
        if full_degrees:
            cap=max(tc[j],T-tc[j])+1
            assert all(deg(h)<=cap for h in H)
            if f:
                assert any(H)
                assert all(not h or deg(h)>=alpha for h in H)
                if abs(2*tc[j]-T)<=1:
                    assert alpha<=cap and T>=2*alpha-3
        count+=1;covector_checks+=width
        if j==len(ops):break
        g=ops[j]
        # Boolean secant matrix inverse transport; endpoints before the gate.
        if g[0]=='C':
            a,t=g[1:];lam[a]^=lam[t]
        elif g[0]=='T':
            a,b,t=g[1:]; lt=lam[t]
            lam[a]^=lt & ao[j][b]
            lam[b]^=lt & az[j][a]
    return count,covector_checks,T
