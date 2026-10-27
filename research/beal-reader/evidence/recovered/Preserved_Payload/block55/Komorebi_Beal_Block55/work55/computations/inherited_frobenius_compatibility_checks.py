#!/usr/bin/env python3
"""Exact finite checks of Block54's local Frobenius/monodromy implications.
The universal result is in notes/FROBENIUS_MONODROMY.md, not this finite grid.
Coefficients are integer pairs a+b*phi, phi^2=phi+1. No floating arithmetic.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path

Z=(0,0); O=(1,0); INF=10**6

def req(x,msg):
    if not x: raise AssertionError(msg)
def add(x,y): return (x[0]+y[0],x[1]+y[1])
def neg(x): return (-x[0],-x[1])
def sub(x,y): return add(x,neg(y))
def mul(x,y):
    a,b=x;c,d=y
    return (a*c+b*d,a*d+b*c+b*d)
def sc(c,x): return (c*x[0],c*x[1])
def vi(a):
    if not a:return INF
    k=0
    while a%7==0:a//=7;k+=1
    return k
def val(x):return min(vi(x[0]),vi(x[1]))
def red(x,M):return (x[0]%M,x[1]%M)
def power(x,e,M):
    z=O;x=red(x,M)
    while e:
        if e&1:z=red(mul(z,x),M)
        x=red(mul(x,x),M);e//=2
    return z
def order7(x,n):
    M=7**n;x=red(x,M)
    req(red(x,7)==O,'unit not principal')
    for k in range(n+1):
        if x==O:return k
        x=power(x,7,M)
    raise AssertionError('principal unit order too large')
def mm(A,B):
    return [[add(mul(A[i][0],B[0][j]),mul(A[i][1],B[1][j])) for j in range(2)] for i in range(2)]
def ms(z,A):return [[mul(z,a) for a in row] for row in A]
def det(A):return sub(mul(A[0][0],A[1][1]),mul(A[0][1],A[1][0]))
ZERO=[[Z,Z],[Z,Z]]

def inspect(N,F,Q,n):
    m=n//2+1;t=min(val(z) for row in N for z in row)
    req(t>=1 and t<INF,'natural content')
    req(mm(N,N)==ZERO and mm(F,N)==ms(Q,N) and mm(N,F)==N,'toric identities')
    req(det(F)==Q and val(Q)==0 and Q!=O,'Frobenius unit determinant')
    req(val(N[1][0])>=n and val(F[1][0])>=n,'common lower-left depth')
    req(val(sub(F[1][1],O))>=m and val(sub(F[0][0],Q))>=m,'global precision')
    j=val(N[0][0]);h=val(sub(Q,O));k=order7(add(O,N[0][0]),n)
    req(j>=m,'inertia half precision')
    if j<n:
        req(k==n-j,'inertia exact order')
        req(k+1<=h,'one tame power loss')
        lift_order=order7(add(O,N[0][0]),n+1)
        req(lift_order==k+1 and lift_order<=h,'local inertia character lift')
    else:req(k==0,'trivial inertia case')
    beta=(val(N[1][0])==n)
    slope=None
    if beta:
        req((n-t)%2==0,'slope parity')
        slope=(n-t)//2
        req(slope>=0 and h>=m and slope<h,'strict supporting-prime bound')
        req(k==slope,'opposite slope equals inertia order exponent')
        req(red(F[0][1],7)==Z,'natural local extension zero')
    if n==3 and k>0:
        req(beta and t==1 and slope==1,'depth3 eta ramification bridge')
    return {'beta':beta,'k':k,'s':slope,'h':h,'m':m,'t':t}

def main(out):
    units=[(1,0),(0,1),(2,1),(1,1)]
    count=nonrational=beta=ram=beta_ram=unram_beta_ram_eta=tight_norm=tight_loss=0
    # Primitivity, the common depth and the diagonal congruence are generated;
    # all matrix identities and the NEW consequences are independently tested.
    for n,t,s,x,uy,da,db in itertools.product(range(1,10),range(1,7),range(7),units,units[:2],range(2),range(2)):
        if t+2*s<n:continue
        y=sc(7**s,uy);mu=sc(7**t,(1,1))
        p=sc(7**(max(n-s,0)+da),(2,1))
        r=sc(7**(max(n//2+1-s,0)+db),(1,0))
        Q=add(O,add(mul(p,x),mul(r,y)))
        if val(Q)!=0 or Q==O:continue
        N=ms(mu,[[neg(mul(x,y)),mul(x,x)],[neg(mul(y,y)),mul(x,y)]])
        F=[[add(O,mul(x,p)),mul(x,r)],[mul(y,p),add(O,mul(y,r))]]
        z=inspect(N,F,Q,n);count+=1
        nonrational+=int(any(a[1] for A in (N,F) for row in A for a in row))
        beta+=int(z['beta']);ram+=int(z['k']>0)
        beta_ram+=int(z['beta'] and z['k']>0)
        unram_beta_ram_eta+=int(not z['beta'] and z['k']>0)
        tight_norm+=int(z['beta'] and z['h']==z['m'])
        tight_loss+=int(z['k']>0 and z['h']==z['k']+1)
    # Separately cover nonunit first coordinates, including x=0, y unit.
    special=0
    for n,x,uy,punit,runit in itertools.product(range(1,10),[(0,0),(7,0),(0,7)],units[:2],units[:2],units[:2]):
        y=uy;t=n;mu=sc(7**t,O);p=sc(7**n,punit);r=sc(7**(n//2+1),runit)
        Q=add(O,add(mul(p,x),mul(r,y)))
        if Q==O or val(Q)!=0:continue
        N=ms(mu,[[neg(mul(x,y)),mul(x,x)],[neg(mul(y,y)),mul(x,y)]])
        F=[[add(O,mul(x,p)),mul(x,r)],[mul(y,p),add(O,mul(y,r))]]
        inspect(N,F,Q,n);special+=1
    # Rational norm Q=491 (491 splits in K); h=2, depth3, slope1 is allowed.
    N=[[(-49,0),(7,0)],[(-343,0),(49,0)]]
    F=[[(1,0),(70,0)],[(0,0),(491,0)]]
    tight491=inspect(N,F,(491,0),3)
    req(491%5 in (1,4) and 197%5 in (2,3),'K residue-degree normalization')
    # The old abstract Q29 example is valid under the OLD hypotheses, but
    # fails the new diagonal precision. Preserve rather than retract it.
    F29=[[(1,0),(4,0)],[(0,0),(29,0)]]
    req(mm(F29,N)==ms((29,0),N) and mm(N,F29)==N,'old example changed')
    req(val(sub(F29[1][1],O))==1<2,'old example unexpectedly passes precision')
    req(red(F29[0][1],7)!=(0,0),'old nonzero local alpha lost')
    # Without natural content t>=1, n=2,m=2,h=1 can pass diagonal precision.
    # x=1,y=7,p=7,r=0 gives Q=8, d=1 and F21=49, but a-Q=0.
    N0=[[(-7,0),(1,0)],[(-49,0),(7,0)]]
    F0=[[(8,0),(0,0)],[(49,0),(1,0)]]
    req(mm(N0,N0)==ZERO and mm(F0,N0)==ms((8,0),N0) and mm(N0,F0)==N0,'t0 counterexample')
    req(val(N0[1][0])==2 and val(F0[1][0])==2 and vi(8-1)==1,'t0 counterexample valuations')
    req(val(sub(F0[1][1],O))>=2 and val(sub(F0[0][0],(8,0)))>=2,'t0 precision')
    # Every pair of h and k in this bounded domain: cyclic tame lifts exist
    # exactly below the saturated order, independently of matrix generation.
    cyclic=0;blocked=0
    for n in range(2,8):
        for j in range(1,n):
            for h in range(0,8):
                z=(1+7**j,0);k=n-j
                req(order7(z,n)==k and order7(z,n+1)==k+1,'scalar unit order')
                if k<=h:
                    req((power(z,7**h,7**(n+1))==O)==(k<h),'tame lift capacity')
                    cyclic+=1;blocked+=int(k==h)
    # Exact rational-prime congruence enumeration modulo 5*49.
    residues=[a for a in range(245) if a%5 in (1,4) and a%49==1 or a%5 in (2,3) and a%49 in (1,48)]
    req(residues==[1,48,97,99,148,197],'CRT residue set')
    req(unram_beta_ram_eta>0 and tight_norm>0 and tight_loss>0,'missing discriminating regimes')
    result={'status':'PASS','coefficient_ring':'Z[phi], phi^2=phi+1; exact integers',
      'generated_grid_cases':count,'nonrational_cases':nonrational,
      'nonunit_first_coordinate_cases':special,'beta_ramified_cases':beta,
      'eta_ramified_cases':ram,'both_ramified_cases':beta_ram,
      'beta_unramified_eta_ramified_cases':unram_beta_ram_eta,
      'tight_support_norm_cases':tight_norm,'tight_capacity_loss_cases':tight_loss,
      'split_K_norm_491_example':tight491,'cyclic_tame_cases':cyclic,
      'saturated_nonliftable_negative_controls':blocked,
      'other_negative_controls':['Q29 old example fails new precision','natural content zero breaks strengthened bound'],
      'rational_residues_mod245':residues,
      'nonclaims':['Generated coefficient-ring Q values are not all residue norms',
                   'Local matrices are not global Frey representations',
                   'No finite test proves the global cohomological injectivity theorem']}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();main(a.output)
