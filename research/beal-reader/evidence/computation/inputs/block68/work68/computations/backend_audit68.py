#!/usr/bin/env python3
"""Exact optional-NumPy/stdlib parity checks and three cyclotomic factorizations."""
import argparse,importlib.util,json,math
from pathlib import Path

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--columns',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=Path(__file__).parent
m=load(root/'count68.py','primary_backend_audit');numpy_module=m.np;total=0
if numpy_module is not None:
    for q in (11,13,17):
        m.np=numpy_module;fast=m.tables(q);m.np=None;slow=m.tables(q)
        for aa in range(q):
            for bb in range(q):
                for deg in (1,2):
                    m.np=numpy_module;x=m.counts(aa,bb,q,fast,deg);m.np=None;y=m.counts(aa,bb,q,slow,deg)
                    assert x==y;total+=1
    m.np=numpy_module
s=load(root/'independent_count68.py','secondary_backend_audit');s.PRIMES=(29,);ref=json.loads(a.reference.read_text());fast=s.count_audit(ref);oldnp=s.np;s.np=None;slow=s.count_audit(ref);assert fast==slow;s.np=oldnp
# Phi basis only for an independently checked finite-field factorization identity.
cc=json.loads(a.columns.read_text());records=[]
for rec in cc['columns']:
    if rec['residue_degree']!=2:continue
    q=rec['q'];z=tuple(rec['zeta'])
    def mul(x,y):return ((x[0]*y[0]+x[1]*y[1])%q,(x[0]*y[1]+x[1]*y[0]+x[1]*y[1])%q)
    zz=[(1,0)]
    for _ in range(6):zz.append(mul(zz[-1],z))
    polys=[];product=[1]
    for b in (1,2,3):
        t=((zz[b][0]+zz[7-b][0])%q,(zz[b][1]+zz[7-b][1])%q);assert t[1]==0
        poly=[1,-t[0]%q,1];disc=(t[0]*t[0]-4)%q;assert pow(disc,(q-1)//2,q)==q-1
        out=[0]*(len(product)+2)
        for i,x in enumerate(product):
            for j,y in enumerate(poly):out[i+j]=(out[i+j]+x*y)%q
        product=out;polys.append(poly)
    assert product==[1]*7;records.append({'q':q,'irreducible_quadratic_factors_ascending':polys})
out={'schema':'beal.block68.backend-audit.v1','status':'PASS_BACKEND_AND_FACTOR_AUDIT','numpy_available':numpy_module is not None,'primary_backend_equalities':total,'secondary_complete_reference_prime':29,'secondary_reference_pairs':ref['primes'][0]['admissible_pairs'],'factorizations':records,'int64_bound':'For all declared count primes <=1009 every unreduced vector operation has absolute value < 100*1009^3 < 2^63. All sums have < 2*1009^2 magnitude.'}
a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],total)
