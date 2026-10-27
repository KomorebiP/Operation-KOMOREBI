#!/usr/bin/env python3
import sympy as sp
from fractions import Fraction as F
from math import comb
import json,time,sys,platform
from pathlib import Path
BASE=Path(__file__).resolve().parent

def v2i(n):
    if n==0:return 10**9
    n=abs(int(n)); return (n&-n).bit_length()-1

def v2f(q): return v2i(q.numerator)-v2i(q.denominator)
def bernF(n):
    b=sp.bernoulli(n); return F(int(sp.numer(b)),int(sp.denom(b)))
def kappa(m): return -F(2**(4*m)*(2*m-1))*bernF(2*m) if m else F(1)
def source(q): return F(3**(2*q+2)-1,4*(2*q+1)*(2*q+2))
def lam(r,j): return 3*j+(r+j).bit_count()-r.bit_count()
def mu_for(r):
    B=max(0,(r.bit_count()-1)//3)
    return min(lam(r,j) for j in range(B+1))
def run_case(r,maxx):
    mu=mu_for(r); ks=[kappa(r+j) for j in range(maxx+1)]; rows=[]
    for x in range(maxx+1):
        N=r+x
        tail=sum((ks[j]*comb(2*N,2*(r+j))*source(x-j) for j in range(x+1)),F(0))
        b=v2i(comb(N,r)); a=v2f(tail); base=4*r-1+b+mu
        rows.append({'x':x,'N':N,'binom_v2':b,'tail_v2':a,'G_v2':a-base,'x_mod_4':x%4})
    return {'r':r,'mu':mu,'rows':rows}

t=time.perf_counter()
res={'status':'PASS','python':sys.version,'sympy':sp.__version__,'platform':platform.platform(),
     'cases':[run_case(4093,16),run_case(8189,12)],'runtime_seconds':None}
res['runtime_seconds']=time.perf_counter()-t
# structural assertions
c1=res['cases'][0]['rows']; c2=res['cases'][1]['rows']
assert all(z['G_v2']==1 for z in c1 if z['x']%2==0)
assert all(z['G_v2']==2 for z in c2 if z['x']%2==0)
assert all(z['G_v2']==1 for z in c2 if z['x']%4==3)
(BASE/'RESULTS_EXACT_SMALL_WALLS.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps(res,indent=2))
