#!/usr/bin/env python3
"""Independent conductor audit: direct seventh-power symbols, cyclic norm products,
coefficient field theta^2=theta+1, and explicit Cramer kernel enumeration.
Imports no primary arithmetic. Does not repeat point counts at inherited test primes.
"""
from __future__ import annotations
import argparse,itertools,json,math
from pathlib import Path
GEN={29:(0,0,0,1,-1,-1),43:(-1,-1,-1,-1,-1,1),71:(0,1,-1,-1,1,-1),
211:(-2,-2,-2,-2,1,-1),239:(-2,-2,0,-1,-2,1),491:(0,1,-2,2,0,2),281:(-2,-2,-1,-2,0,1),379:(-2,-2,-1,1,-2,-2)}
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
  q=row['q'];g=row['primitive'];r=row['root'];need(q in record['universe'],'Undeclared conductor column')
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
   for z in itertools.product(range(7),repeat=len(free)):
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
  for x in itertools.product(range(7),repeat=n):
   if any(x):yield list(x)
  return
 i=next(k for k,x in enumerate(row) if x);free=[k for k in range(n) if k!=i];inv=pow(row[i],-1,7)
 for z in itertools.product(range(7),repeat=len(free)):
  x=[0]*n
  for k,c in zip(free,z):x[k]=c
  x[i]=M[inv][minus(dot(row,x))]
  need(all(dot(a,x)==0 for a in rows),'Dependent-row kernel failure')
  if any(x):yield x


def rank7(rows):
    a=[list(r) for r in rows];k=0
    for j in range(len(a[0])):
        i=next((i for i in range(k,len(a)) if a[i][j]%7),None)
        if i is None:continue
        a[i],a[k]=a[k],a[i];iv=pow(a[k][j]%7,-1,7)
        a[k]=[x*iv%7 for x in a[k]]
        for i in range(len(a)):
            if i!=k:
                t=a[i][j];a[i]=[(x-t*y)%7 for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a):break
    return k



def audit_case(case,cols,data):
 conductor=case['conductor'];answer=[];stages=[];total=0
 pairs={e:[{fromw(x) for x in z} for z in zz] for e,zz in data['paired_trace_sets'].items()}
 us=[fromw(7*v) for v in range(1,7)]
 for r in range(1,7):
  C=[q for q in conductor if cols[q]['ratio'] in(r,'all')]
  order=[71,29,491]+([] if 43 in C else[43])+[211,239,281,379]
  rr={l:[cols[q]['rows'][str(l)] for q in C] for l in order};masks={}
  for l in order[2:]:
   masks[l]=[]
   for bb in range(7):
    b=M[2 if l==43 else 1][bb];mask=0
    for j,u in enumerate(us):
     pp=[M[dot(row,[u,r,1])][b] for row in data['kummer_rows'][str(l)]]
     good=any(all(x in pair for x in pp) for pair in pairs[str(l)])
     bad=not any(pp) and (not any(k[0] for k in data['kummer_rows'][str(l)]) or b==0)
     if good or bad:mask|=1<<j
    masks[l].append(mask)
  ns=[(7**(len(C)-rank7([rr[71]]))-1)*6,(7**(len(C)-rank7([rr[71],rr[29]]))-1)*6]+[0]*(len(order)-2)
  count=0
  for x in kernel([rr[71],rr[29]]):
   need(all(0<=v<7 for v in x),'Non-prime-field kernel value');count+=1
   values={l:dot(rr[l],x) for l in order};mask=63
   for j,l in enumerate(order[2:],2):
    mask&=masks[l][values[l]];ns[j]+=mask.bit_count()
    if not mask:break
   if mask:
    for j,u in enumerate(us):
     if mask>>j&1:answer.append({'alpha':[tow(u),r,1],'columns':C,'inertia':x,
       'values':{str(l):values[l] for l in order}})
  need(count*6==ns[1],'Kernel coverage mismatch');total+=count
  stages.append({'ratio':r,'columns':C,'tests':order,'counts':ns})
 canon=lambda x:json.dumps(x,sort_keys=True)
 need(stages==case['stages'],'Independent stage mismatch')
 need(sorted(answer,key=canon)==case['survivors'] and len(answer)==case['count'],'Independent survivor mismatch')
 return {'kernel_vectors':total,'coefficient_character_pairs':6*total,'survivors':len(answer)}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fixture',type=Path,required=True)
 ap.add_argument('--counts',type=Path,required=True);ap.add_argument('--certificate',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 fixture=json.loads(a.fixture.read_text());rec=json.loads(a.certificate.read_text());pc=json.loads(a.counts.read_text())
 U=[q for q in range(11,2001) if q%7==1 and q%5 in(2,3) and all(q%d for d in range(2,math.isqrt(q)+1))]
 need(rec['universe']==U and len(U)==25,'Universe coverage mismatch')
 need([x['q'] for x in rec['columns']]==U,'Missing or duplicate column')
 cols,symbols=columns(rec)
 p=pc['primes'][0];need(len(pc['primes'])==1 and p['q']==379,'Wrong count prime')
 pi=GEN[379];roots=[x for x in range(2,379) if pow(x,7,379)==1 and sum(v*pow(x,j,379) for j,v in enumerate(pi))%379==0]
 need(len(roots)==1 and roots[0]==rec['test379_root']==195,'Incorrect test root')
 root=roots[0];phi=[x for x in range(379) if (x*x-x-1)%379==0];K=[]
 for x in phi:
  K.append([next(j for j in range(7) if pow(root,j,379)==pow(v%379,54,379)) for v in (x,3,2*x-1)])
 need(phi==rec['phi379_roots'] and K==rec['kummer379'],'Changed natural379 symbols')
 fixture['kummer_rows']['379']=K;fixture['good_trace_sets']['379']=p['trace_defect_set']
 fixture['paired_trace_sets']['379']=[list(z) for z in sorted({tuple(t['defect_roots']) for t in p['rows'] if t['residual_pass']})]
 for name in ('kummer_rows','good_trace_sets','paired_trace_sets'):need(fixture[name]==rec[name],'Changed input '+name)
 stats={}
 for name,case in rec['cases'].items():stats[name]=audit_case(case,cols,fixture)
 for t in rec['retained547743_targets']:
  u,r,_=[fromw(x) for x in t['alpha']];b=dot([cols[q]['rows']['379'] for q in t['columns']],t['inertia'])
  ps=[tow(M[dot(k,[u,r,1])][b]) for k in K]
  need(ps==t['products'] and b==t['beta379']==1,'Wrong retained-target evaluation')
  need(not any(all(x in pair for x in ps) for pair in fixture['paired_trace_sets']['379']) and any(ps),'Target not excluded')
  need(not t['good_possible'] and not t['bad_possible'],'False target flag')
 need(rec['larger_conductor_witness'] in rec['cases']['small17_boundary']['survivors'],'Fabricated boundary witness')
 out={'schema':'beal.block65.independent_conductor.v1','status':'PASS_INDEPENDENT_CONDUCTOR',
      'statistics':stats,'direct_seventh_symbols':symbols,'cyclotomic_norms':len(GEN),
      'coefficient_basis':'theta^2=theta+1','primary_arithmetic_imports':False}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(out['status'],stats)
if __name__=='__main__':main()
