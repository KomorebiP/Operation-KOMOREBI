#!/usr/bin/env python3
"""Exact local checks for the maximal-inertia layer lemma. Not a global realization test."""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path
from inherited_frobenius_compatibility_checks import (
    O,Z,add,sub,neg,mul,sc,val,ms,mm,det,order7,inspect,req)

def make(mu,x,y,p,r):
    N=ms(mu,[[neg(mul(x,y)),mul(x,x)],[neg(mul(y,y)),mul(x,y)]])
    F=[[add(O,mul(x,p)),mul(x,r)],[mul(y,p),add(O,mul(y,r))]]
    Q=add(O,add(mul(x,p),mul(y,r)))
    return N,F,Q

def run():
    units=[(1,0),(0,1),(1,1),(2,1)]
    count=beta_unram=nonrational=tight_r=0
    for n in range(3,13):
        m=n//2+1
        for e in range(1,n-m+1):
            L=n-e
            for t in range(1,min(L-1,2*L-n)+1):
                s=L-t
                for x,uy,um,da,db in itertools.product(units,units[:2],units[:2],range(2),range(2)):
                    mu=sc(7**t,um);y=sc(7**s,uy)
                    p=sc(7**(n-s+da),(2,1));r=sc(7**(L-s+db),(1,1))
                    N,F,Q=make(mu,x,y,p,r)
                    z=inspect(N,F,Q,n)
                    req(val(N[0][0])==L and z['k']==e,'maximal inertia order')
                    req(val(sub(F[1][1],O))>=L,'global exponent precision')
                    req(val(F[0][1])>=t>=1,'natural Kummer annihilation')
                    req(val(sub(Q,O))>=e+1,'inherited reduced capacity')
                    count+=1;beta_unram+=int(not z['beta'])
                    nonrational+=int(any(b for A in (N,F) for row in A for _,b in row))
                    tight_r+=int(val(F[0][1])==t)
    req(beta_unram>0 and nonrational==count and tight_r>0,'missing new regime')
    # This genuine split-prime norm disproves annihilation at every ramified
    # eta-place. Its inertia order is below the global exponent bound.
    N,F,Q=make((7,0),O,(343,0),(147,0),O)
    z=inspect(N,F,Q,5)
    req(Q==(491,0) and z['k']==1 and not z['beta'],'negative control local regime')
    req(val(sub(F[1][1],O))==3 and order7(F[1][1],5)==2,'Frobenius order exceeds inertia order')
    req(F[0][1]==O,'negative control must have nonzero local alpha')
    negative={'n':5,'global_exponent_bound':2,'inertia_order_exponent':1,
              'Frobenius_diagonal_order_exponent':2,'N':N,'F':F,'Q':Q,
              'beta_ramified':False,'alpha_Frobenius_mod7':[1,0],
              'meaning':'All-place alpha-zero overstrengthening is false; the maximal-order hypothesis is essential'}
    # Finite field-valued group power calculations in all 48 directions.
    # Raising eta to 7^(e-1) kills exactly elements of order smaller than 7^e.
    powers=0
    from inherited_frobenius_compatibility_checks import power,red
    for n in range(3,10):
        for e in range(1,n-(n//2+1)+1):
            for a,b in itertools.product(range(7),repeat=2):
                if (a,b)==(0,0):continue
                for k in range(1,e+1):
                    v=add(O,sc(7**(n-k),(a,b)))
                    image=power(v,7**(e-1),7**n)
                    req((image==O)==(k<e),'highest layer support')
                    if k==e:req(val(sub(image,O))==n-1,'highest layer precision')
                    powers+=1
    return {'status':'PASS','coefficient_ring':'Z[phi], phi^2=phi+1; exact integer pairs',
            'matrix_cases':count,'nonrational_matrix_cases':nonrational,
            'maximal_eta_ramified_beta_unramified_cases':beta_unram,
            'tight_natural_upper_right_valuation_cases':tight_r,
            'highest_layer_power_cases':powers,'negative_control':negative,
            'ranges':{'n':[3,12],'e':'1..n-floor(n/2)-1','t':'1..min(n-e-1,n-2e)'},
            'nonclaims':['Generated Q need not be a residue norm, except specified Q491 control',
                         'The local examples are not global Frey representations',
                         'Finite counts do not prove the universal theorem']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    out=run();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2))
