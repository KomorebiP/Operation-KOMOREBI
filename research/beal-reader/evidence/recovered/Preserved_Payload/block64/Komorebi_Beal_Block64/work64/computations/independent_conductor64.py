#!/usr/bin/env python3
"""Independent conductor audit: direct seventh-power symbols, cyclic norm products,
coefficient field theta^2=theta+1, and explicit Cramer kernel enumeration.
Imports no primary arithmetic. Does not repeat point counts at inherited test primes.
"""
from __future__ import annotations
import argparse,itertools,json,math
from pathlib import Path
GEN={29:(0,0,0,1,-1,-1),43:(-1,-1,-1,-1,-1,1),71:(0,1,-1,-1,1,-1),
211:(-2,-2,-2,-2,1,-1),239:(-2,-2,0,-1,-2,1),491:(0,1,-2,2,0,2),281:(-2,-2,-1,-2,0,1)}
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
  q=row['q'];g=row['primitive'];r=row['root'];need(q in W+(617,743,953),'Undeclared conductor column')
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
    conductor=case['conductor'];joint=case['joint_good_polynomial'];extra=case['includes281']
    allgood={e:{fromw(x) for x in z} for e,z in data['good_trace_sets'].items()}
    pairgood={e:[{fromw(x) for x in z} for z in zz] for e,zz in data['paired_trace_sets'].items()}
    answers=[];stages=[];vectors=0;weighted_pairs=0
    for r in range(1,7):
        C=[q for q in conductor if cols[q]['ratio'] in (r,'all')]
        order=[71,29,491]+([] if 43 in C else [43])+[211,239]+([281] if extra else [])
        rr={l:[cols[q]['rows'][str(l)] for q in C] for l in order}
        masks={}
        for l in order[2:]:
            masks[l]=[]
            kr=data['kummer_rows'][str(l)]
            for bb in range(49):
                beta=M[2 if l==43 else 1][bb];mask=0
                for u in range(1,49):
                    ps=[M[dot(row,[u,r,1])][beta] for row in kr]
                    good=(any(all(x in pair for x in ps) for pair in pairgood[str(l)]) if joint
                          else all(x in allgood[str(l)] for x in ps))
                    bad=not any(ps) and (not any(row[0] for row in kr) or beta==0)
                    if good or bad:mask|=1<<u
                masks[l].append(mask)
        ns=[(49**(len(C)-rank7([rr[71]]))-1)*48,
            (49**(len(C)-rank7([rr[71],rr[29]]))-1)*48]+[0]*(len(order)-2)
        local_vectors=0
        for x in kernel([rr[71],rr[29]]):
            local_vectors+=1;values={l:dot(rr[l],x) for l in order};mask=(1<<49)-2
            for j,l in enumerate(order[2:],2):
                mask&=masks[l][values[l]];ns[j]+=mask.bit_count()
                if not mask:break
            if mask:
                for u in range(1,49):
                    if mask>>u&1:
                        answers.append({'alpha':[tow(u),r,1],'columns':C,'inertia':[tow(v) for v in x],
                            'values':{str(l):tow(values[l]) for l in order}})
        need(local_vectors*48==ns[1],'Kernel cardinality disagrees')
        stages.append({'ratio':r,'columns':C,'tests':order,'counts':ns})
        vectors+=local_vectors;weighted_pairs+=local_vectors*48
    canon=lambda rows:sorted(json.dumps(x,sort_keys=True) for x in rows)
    need(stages==case['stages'],'Independent stage counts differ')
    need(canon(answers)==canon(case['survivors']) and len(answers)==case['count'],'Independent survivor list differs')
    return {'kernel_vectors_enumerated':vectors,'coefficient_vector_pairs_covered':weighted_pairs,
            'survivors':len(answers),'count_method':'Every kernel vector; exact bitsets for48 nonzero coefficients'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fixture',type=Path,required=True);ap.add_argument('--counts',type=Path,required=True)
    ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();fixture=json.loads(a.fixture.read_text());rec=json.loads(a.certificate.read_text())
    pc=json.loads(a.counts.read_text());new=pc['primes'][0]
    need(new['q']==281,'Wrong count prime')
    cols,symbols=columns(rec)
    # Independent prime generator and Kummer normalization at281.
    pi=GEN[281];roots=[x for x in range(2,281) if pow(x,7,281)==1 and sum(c*pow(x,j,281) for j,c in enumerate(pi))%281==0]
    need(len(roots)==1 and roots[0]==rec['test281_root'],'Wrong281 prime generator/root')
    root=roots[0];phi=[x for x in range(281) if (x*x-x-1)%281==0]
    kr=[]
    for x in phi:
        row=[]
        for v in (x,3,2*x-1):
            sym=pow(v%281,40,281);row.append(next(i for i in range(7) if pow(root,i,281)==sym))
        kr.append(row)
    need(kr==rec['kummer281'] and phi==rec['phi281_roots'],'Changed281 Kummer coordinates')
    fixture['kummer_rows']['281']=kr;fixture['good_trace_sets']['281']=new['trace_defect_set']
    fixture['paired_trace_sets']['281']=[list(z) for z in sorted({tuple(x['defect_roots']) for x in new['rows'] if x['residual_pass']})]
    need(fixture['good_trace_sets']==rec['good_trace_sets'] and fixture['paired_trace_sets']==rec['paired_trace_sets'],'Changed source trace sets')
    need(fixture['good_trace_sets']['29']==[2] and fixture['kummer_rows']['29']==[[4,1,5],[3,1,5]],'Unjustified29 shortcut')
    stats={}
    for name,case in rec['cases'].items():
        stats[name]=audit_case(case,cols,fixture);print(name,stats[name],flush=True)
    # Re-evaluate old exact target in the alternate coefficient field.
    for t in rec['target617_evaluations']:
        u,r,_=[fromw(x) for x in t['alpha']]
        b=6;prod=[tow(M[dot(k,[u,r,1])][b]) for k in kr]
        need(prod==t['products'] and t['beta281']==6,'Wrong617 contradiction values')
        need(not t['good_possible'] and not t['bad_possible'],'Invented surviving617 tuple')
    # Twisted-root orientation: the13 row supplies no independent value on this descended regime.
    out={'schema':'beal.block64.independent_conductor.v1','status':'PASS_INDEPENDENT_CONDUCTOR',
         'statistics':stats,'cyclotomic_norms':len(GEN),'direct_seventh_symbols':symbols,
         'natural281_symbols':6,'coefficient_field':'theta^2=theta+1','primary_arithmetic_imports':False,
         'scope':'Exact finite arithmetic, not an independent mathematical review or Frey realization.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'])
if __name__=='__main__':main()
