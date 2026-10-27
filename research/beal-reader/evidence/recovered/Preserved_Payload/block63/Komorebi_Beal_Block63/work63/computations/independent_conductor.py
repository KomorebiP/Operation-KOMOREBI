#!/usr/bin/env python3
"""Independent conductor audit: direct seventh-power symbols, cyclic norm products,
coefficient field theta^2=theta+1, and explicit Cramer kernel enumeration.
Imports no primary arithmetic. Does not repeat point counts at inherited test primes.
"""
from __future__ import annotations
import argparse,itertools,json,math
from pathlib import Path
GEN={29:(0,0,0,1,-1,-1),43:(-1,-1,-1,-1,-1,1),71:(0,1,-1,-1,1,-1),
211:(-2,-2,-2,-2,1,-1),239:(-2,-2,0,-1,-2,1),491:(0,1,-2,2,0,2)}
W=(43,113,127,197,337,463,547,883,1373,1667)
def need(ok,msg):
 if not ok:raise AssertionError(msg)
def plus(x,y):return (x%7+y%7)%7+7*((x//7+y//7)%7)
def times(x,y):
 a,b=x%7,x//7;c,d=y%7,y//7
 return (a*c+b*d)%7+7*((a*d+b*c+b*d)%7)
def minus(x):return (-x%7)%7+7*((-(x//7))%7)
def diff(x,y):return plus(x,minus(y))
def fromw(x):return (x%7-x//7)%7+7*(2*(x//7)%7)
def tow(x):return (x%7+4*(x//7))%7+7*(4*(x//7)%7)
A=[[plus(x,y) for y in range(49)] for x in range(49)]
M=[[times(x,y) for y in range(49)] for x in range(49)]
def dot(a,b):
 v=0
 for x,y in zip(a,b):v=A[v][M[x][y]]
 return v
def norm(a):
 # Multiply the six conjugates in Z[zeta]/(zeta^7-1), then set Phi_7=0.
 v=[1]+[0]*6
 for j in range(1,7):
  b=[0]*7
  for i,c in enumerate(a):b[i*j%7]+=c
  w=[0]*7
  for x in range(7):
   for y in range(7):w[(x+y)%7]+=v[x]*b[y]
  v=w
 out=[v[i]-v[6] for i in range(6)];need(all(x==0 for x in out[1:]),'Norm not rational')
 return out[0]
def columns(record):
 direct=0;out={}
 for ell,a in GEN.items():need(norm(a)==ell,'Incorrect cyclotomic norm')
 for row in record['columns']:
  q=row['q'];g=row['primitive'];r=row['root'];need(q in W+(617,),'Undeclared conductor column')
  need(all(q%d for d in range(2,math.isqrt(q)+1)) and q%5 in(2,3) and q%7==1,'Prime/descent regime')
  fac=[d for d in range(2,q) if (q-1)%d==0 and all(d%e for e in range(2,math.isqrt(d)+1))]
  need(all(pow(g,(q-1)//d,q)!=1 for d in fac),'Nonprimitive generator')
  need(r==pow(g,(q-1)//7,q) and r!=1,'Wrong residue root')
  powers={pow(r,j,q):j for j in range(7)}
  def log7(x):
   need(x%q!=0,'Nonunit in residue-symbol computation')
   return powers[pow(x,(q-1)//7,q)]
  rr={}
  for ell,aa in GEN.items():
   if ell==q:continue
   tt=[0]*7
   for j,c in enumerate(aa):tt[-j%7]+=c  # theta=zeta^-1
   vals=[];logs=[]
   for b in range(1,7):
    z=pow(r,(-b)%7,q);v=sum(c*pow(z,j,q) for j,c in enumerate(tt))%q
    vals.append(v);logs.append(log7(v));direct+=1
   rr[str(ell)]=-sum(j*x for j,x in enumerate(logs,1))%7
   need(vals==row['symbols'][str(ell)]['values'] and logs==row['symbols'][str(ell)]['logs_mod7'],'Changed symbol data')
  kk=[0,2*log7(3)%7,log7(5)];ratio=(-kk[2]*pow(kk[1],-1,7))%7 if kk[1] else ('all' if kk[2]==0 else 'none')
  need(rr==row['rows'] and kk==row['kummer'] and ratio==row['ratio'],'Changed twisted row or Kummer ratio')
  out[q]={'rows':rr,'ratio':ratio}
 return out,direct

def kernel(rows):
 n=len(rows[0])
 if len(rows)==2:
  a,b=rows;pair=next(((i,j) for i in range(n) for j in range(i+1,n) if (a[i]*b[j]-a[j]*b[i])%7),None)
  if pair:
   i,j=pair;iv=pow((a[i]*b[j]-a[j]*b[i])%7,-1,7);free=[k for k in range(n) if k not in pair]
   for z in itertools.product(range(49),repeat=len(free)):
    x=[0]*n
    for k,c in zip(free,z):x[k]=c
    aa=minus(dot(a,x));bb=minus(dot(b,x))
    x[i]=M[iv][diff(M[b[j]][aa],M[a[j]][bb])]
    x[j]=M[iv][diff(M[a[i]][bb],M[b[i]][aa])]
    need(dot(a,x)==dot(b,x)==0,'Cramer kernel failure')
    if any(x):yield x
   return
  # Dependent or zero rows: use either nonzero row, with all constraints checked.
 row=next((a for a in rows if any(a)),None)
 if row is None:
  for x in itertools.product(range(49),repeat=n):
   if any(x):yield list(x)
  return
 i=next(k for k,x in enumerate(row) if x);free=[k for k in range(n) if k!=i];inv=pow(row[i],-1,7)
 for z in itertools.product(range(49),repeat=len(free)):
  x=[0]*n
  for k,c in zip(free,z):x[k]=c
  x[i]=M[inv][minus(dot(row,x))]
  need(all(dot(a,x)==0 for a in rows),'Dependent-row kernel failure')
  if any(x):yield x

def run_sieve(conductor,cols,data,nonzero):
 good={e:{fromw(x) for x in vals} for e,vals in data['good_trace_sets'].items()}
 nat=data['kummer_rows'];answer=[];vectors=0;tuples=0
 for r in range(1,7):
  C=[q for q in conductor if cols[q]['ratio'] in(r,'all')]
  order=[29,491]+([] if 43 in C else [43])+[211,239]
  rr={ell:[cols[q]['rows'][str(ell)] for q in C] for ell in [71]+order}
  constraints=[rr[71]]+([rr[29]] if nonzero else [])
  for x in kernel(constraints):
   vectors+=1;vals={ell:dot(rr[ell],x) for ell in order}
   for u in range(1 if nonzero else 0,49):
    tuples+=1;passes=True
    for ell in order:
     beta=M[2 if ell==43 else 1][vals[ell]]
     prods=[M[dot(row,[u,r,1])][beta] for row in nat[str(ell)]]
     g=all(y in good[str(ell)] for y in prods)
     b=all(y==0 for y in prods) and (not any(row[0] for row in nat[str(ell)]) or beta==0)
     if not(g or b):passes=False;break
    if passes:
     answer.append({'alpha':[tow(u),r,1],'columns':C,'inertia':[tow(y) for y in x],
                    'values':{str(e):tow(dot(rr[e],x)) for e in [71]+order}})
 return answer,{'kernel_vectors':vectors,'coefficient_vector_pairs':tuples}
def canon(xs):return sorted(json.dumps(x,sort_keys=True) for x in xs)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 data=json.loads(a.fixture.read_text());record=json.loads(a.certificate.read_text());cols,n=columns(record)
 # The u!=0 implication beta29=0 follows from two differing natural values and G29={2}.
 need(data['good_trace_sets']['29']==[2] and data['kummer_rows']['29']==[[4,1,5],[3,1,5]],'Invalid early two-row reduction')
 stats={}
 for name,C,nonzero in [('strict',W,True),('without_unit_restriction',W,False),('outside_617_control',tuple(sorted(W+(617,))),True)]:
  ans,st=run_sieve(C,cols,data,nonzero)
  need(canon(ans)==canon(record[name]['survivors']) and len(ans)==record[name]['count'],'Changed finite sieve claim')
  st['survivors']=len(ans);stats[name]=st
  print(name,st,flush=True)
 out={'schema':'beal.block63.independent_conductor.v1','status':'PASS_INDEPENDENT_CONDUCTOR',
      'direct_seventh_symbols':n,'cyclotomic_norms':6,'coefficient_field':'theta^2=theta+1',
      'statistics':stats,'primary_imports':False,'nonclaim':'Not an independent mathematical reviewer or a global realization test.'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
