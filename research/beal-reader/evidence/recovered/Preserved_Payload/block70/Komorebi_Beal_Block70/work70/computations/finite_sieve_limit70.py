#!/usr/bin/env python3
"""Construct an explicit nonzero abstract character escaping every fixed trace row.
This is not a Frey representation or an integer solution. It certifies the linear
limitation of the finite zero-or-good tests when larger conductor is allowed.
"""
from pathlib import Path
import argparse,json,math
from columns68 import column

def sieve_primes(n):
 a=bytearray(b'\1')*(n+1);a[:2]=b'\0\0'
 for p in range(2,math.isqrt(n)+1):
  if a[p]:a[p*p:n+1:p]=b'\0'*(((n-p*p)//p)+1)
 return [i for i in range(2,n+1) if a[i]]
def kernel(A):
 B=[[x%7 for x in row] for row in A];m=len(B);n=len(B[0]);piv=[];i=0
 for j in range(n):
  k=next((k for k in range(i,m) if B[k][j]),None)
  if k is None:continue
  B[i],B[k]=B[k],B[i];c=pow(B[i][j],-1,7);B[i]=[c*x%7 for x in B[i]]
  for k in range(m):
   if k!=i:
    c=B[k][j];B[k]=[(x-c*y)%7 for x,y in zip(B[k],B[i])]
  piv.append(j);i+=1
  if i==m:break
 free=next(j for j in range(n) if j not in piv);v=[0]*n;v[free]=1
 for k,j in enumerate(piv):v[j]=-B[k][free]%7
 assert any(v) and all(sum(x*y for x,y in zip(row,v))%7==0 for row in A)
 return v,len(piv)
def main():
 p=argparse.ArgumentParser();p.add_argument('--fixture',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();d=json.loads(a.fixture.read_text());tests=d['test_order'];wanted=len(tests)+1
 qs=[]
 for q in sieve_primes(500000):
  if q<=3000 or q in tests or q%7!=1 or q%5 not in(2,3):continue
  if pow(3,(q-1)//7,q)==1 and pow(5,(q-1)//7,q)==1:qs.append(q)
  if len(qs)==wanted:break
 assert len(qs)==wanted,'Finite witness search insufficient; no infinite theorem inferred from this scan'
 cc=[column(q,d) for q in qs];assert all(x['kummer']==[0,0,0] for x in cc)
 A=[[c['rows'][str(t)] for c in cc] for t in tests];v,rank=kernel(A)
 controls=[]
 for q,t in zip(qs,v):
  if not t:continue
  A0=pow(75,-1,q);B0=pow((-pow(A0,3,q))%q,pow(5,-1,q-1),q)
  assert (pow(A0,3,q)+pow(B0,5,q))%q==0 and (5*pow(B0,4,q))%q
  controls.append({'q':q,'inertia':t,'A_mod_q':A0,'B_mod_q':B0,'C_valuation':1,'meaning':'Local level-seven period test passes. Hensel defines B locally for C=q. Not a global integer B or common representation.'})
 out={'schema':'beal.block70.finite_sieve_limit.v1','status':'PASS_ABSTRACT_ESCAPE_CERTIFICATE','test_order':tests,'conductor_primes':qs,'columns':cc,'matrix':A,'rank':rank,'nullity':len(qs)-rank,'inertia':v,'nonzero_support':controls,'alpha_w_codes':[7,6,1],'all_test_values':[sum(x*y for x,y in zip(row,v))%7 for row in A],
 'scope':'Abstract descended inverse-cyclotomic character in the inherited ray-class model, with all natural Kummer rows zero on its support and all specified Frobenius values zero. It escapes the fixed homogeneous zero-or-good trace constraints. It does not realize the full actual representation, an integer triple, or every possible future constraint.',
 'prime_search_bound':500000,'infinite_statement':'The separate written proof uses Chebotarev and ray-class theory; this finite witness is not its proof.'}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('PASS_ESCAPE_CERTIFICATE',len(tests),'rows',len(qs),'columns','rank',rank,'nonzero',len(controls),'range',qs[0],qs[-1],flush=True)
if __name__=='__main__':main()
