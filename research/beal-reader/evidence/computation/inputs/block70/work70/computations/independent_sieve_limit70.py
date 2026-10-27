#!/usr/bin/env python3
"""Independent weighted-product and vector audit of the abstract escape certificate."""
from pathlib import Path
import argparse,json,math
from independent_columns68 import product_norm,divisors

def need(x,s):
 if not x:raise AssertionError(s)
def times(x,y,q):
 a,b=x;c,d=y;return ((a*c+5*b*d)%q,(a*d+b*c)%q)
def power(x,n,q):
 y=(1,0)
 for b in bin(n)[2:]:
  y=times(y,y,q)
  if b=='1':y=times(y,x,q)
 return y

def main():
 p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--certificate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();f=json.loads(a.fixture.read_text());d=json.loads(a.certificate.read_text());tests=f['test_order'];qs=d['conductor_primes'];vv=d['inertia']
 need(d['test_order']==tests and len(qs)==len(tests)+1,'Wrong fixed-row certificate dimension')
 need(len(qs)==len(set(qs)) and len(vv)==len(qs) and any(vv),'Missing nonzero enlarged-conductor vector')
 for k,cs in f['generators'].items():need(product_norm(cs)==int(k),'Bad integral test-prime norm')
 columns=[];symbols=0;units=0
 for q,record in zip(qs,d['columns']):
  need(q>3000 and q not in tests and q%7==1 and q%5 in(2,3) and all(q%d for d in range(2,math.isqrt(q)+1)),'Invalid new conductor prime')
  g=next(g for g in range(2,q) if all(pow(g,(q-1)//p,q)!=1 for p in divisors(q-1)));z=pow(g,(q-1)//7,q)
  need(record['q']==q and record['generator']==[g,0] and record['zeta']==[z,0],'Wrong escape-column normalization')
  def symbol(x):
   need(x%q!=0,'Nonunit at enlarged conductor');s=pow(x,(q-1)//7,q)
   return next(i for i in range(7) if pow(z,i,q)==s)
  def row(cs):
   prod=1
   for b in range(1,7):
    root=pow(z,b,q);value=sum(c*pow(root,i,q) for i,c in enumerate(cs))%q;prod=prod*pow(value,b,q)%q
   return -symbol(prod)%7
  entries={str(t):row(f['generators'][str(t)]) for t in tests};need(entries==record['rows'],'Changed abstract escape row');symbols+=6*len(tests)
  need(pow(3,(q-1)//7,q)==pow(5,(q-1)//7,q)==1,'Nonzero natural Kummer residue')
  phi=(pow(2,-1,q),pow(2,-1,q));need(power(phi,q+1,q)==(q-1,0),'Wrong inert phi norm');need(power(phi,(q*q-1)//7,q)==(1,0),'Phi is not a seventh power')
  need(power((0,1),(q*q-1)//7,q)==(1,0),'Base radical is not a seventh power')
  for j in range(1,7):need(row([1]*j)==0,'Unit projection not zero');units+=1
  columns.append(entries)
 A=[[c[str(t)] for c in columns] for t in tests];need(A==d['matrix'],'Changed full escape matrix')
 vals=[sum(v*x for v,x in zip(vv,row))%7 for row in A];need(vals==[0]*len(tests) and vals==d['all_test_values'],'Escape vector does not annihilate every fixed row')
 rr=[r[:] for r in A];rank=0
 for j in range(len(qs)):
  nz=[i for i in range(rank,len(rr)) if rr[i][j]%7]
  if not nz:continue
  rr[rank],rr[nz[0]]=rr[nz[0]],rr[rank];pivot=rr[rank][j]
  for i in range(rank+1,len(rr)):
   scale=rr[i][j];rr[i]=[(pivot*x-scale*y)%7 for x,y in zip(rr[i],rr[rank])]
  rank+=1
 need(rank==d['rank'] and len(qs)-rank==d['nullity'],'Changed escape matrix rank')
 controls=d['nonzero_support'];need([x['q']for x in controls]==[q for q,v in zip(qs,vv)if v],'Changed nonzero conductor support')
 for x in controls:
  q=x['q'];A0=x['A_mod_q'];B0=x['B_mod_q'];need(75*A0%q==1 and (pow(A0,3,q)+pow(B0,5,q))%q==0,'False local period/fifth-root control');need((5*pow(B0,4,q))%q!=0,'Invalid Hensel derivative')
 out={'schema':'beal.block70.independent_sieve_limit.v1','status':'PASS_SEPARATE_ABSTRACT_ESCAPE','rows':len(tests),'columns':len(qs),'rank':rank,'nonzero_support':len(controls),'direct_weighted_symbol_evaluations':symbols,'unit_checks':units,'matrix_values':vals,'primary_arithmetic_imports':False,'nonclaim':'No global Frey representation or integer solution constructed.'}
 a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print('PASS_SEPARATE_ABSTRACT_ESCAPE',rank,len(controls),flush=True)
if __name__=='__main__':main()
