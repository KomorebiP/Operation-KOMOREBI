#!/usr/bin/env python3
"""Separate target-count audit with explicit square roots and independent curve labels.
No primary arithmetic imports. Reconstructs every demand/skip decision, every
count made, all target products, and complete admissible-pair coverage.
"""
from __future__ import annotations
import argparse,hashlib,json,math,os,sys,collections
from pathlib import Path
sys.dont_write_bytecode=True
import independent_count68 as core
np=core.np

def check(ok,msg):
 if not ok:raise AssertionError(msg)
def ident(s):return hashlib.sha256(json.dumps(s,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def mul(x,y,p):
 a,b=x;c,d=y
 return ((a*c+b*d)%p,(a*d+b*c+b*d)%p)
def powpair(x,n,p):
 y=(1,0)
 while n:
  if n&1:y=mul(y,x,p)
  x=mul(x,x,p);n//=2
 return y
def wcode(x):return (x[0]+4*x[1])%7+7*(4*x[1]%7)

def audit(data,sieve,fixture,colcert):
 rec=data['record'];q=rec['q'];p=q
 check(q>2000 and q%7==1 and q%5 in (1,4),'Test not in stated unramified/split regime')
 check(all(q%d for d in range(2,math.isqrt(q)+1)),'Nonprime test')
 check(len(sieve['survivors'])==18 and sieve['survivor_count']==18,'Changed frozen candidate cover')
 check(colcert['status']=='PASS_SEPARATE_COLUMN_AUDIT','Unverified separate columns')
 cr={c['q']:c for c in colcert['rows']};cs=fixture['generators'][str(q)]
 zr=[z for z in range(2,q) if pow(z,7,q)==1 and sum(c*pow(z,i,q) for i,c in enumerate(cs))%q==0]
 check(len(zr)==1,'Bad test-prime generator');zeta=zr[0]
 def log(x):
  y=pow(x%q,(q-1)//7,q)
  return next(i for i in range(7) if pow(zeta,i,q)==y)
 phis=[x for x in range(q) if (x*x-x-1)%q==0];check(len(phis)==2,'Nonsplit test')
 kr=[[log(x),log(3),log(2*x-1)] for x in phis]
 check(kr==fixture['kummer_rows'][str(q)],'Changed natural residue row')
 ts=[]
 for s in sieve['survivors']:
  check(q not in s['columns'],'Ramified test place not handled')
  v=s['alpha'][0]//7;r=s['alpha'][1]
  b=sum(t*cr[c]['rows'][str(q)] for c,t in zip(s['columns'],s['inertia']))%7
  u=(-v%7,2*v%7);pp=[]
  for x,y,z in kr:
   t=mul((x,0),u,7);t=((t[0]+y*r+z)%7,t[1]);pp.append(wcode(mul((b,0),t,7)))
  if any(pp):
   a=pp[0]%7;e=pp[0]//7;sig=[2*a%7,(a*a-5*e*e)%7];key=f'{sig[0]},{sig[1]}'
   check(pp[1]==a+7*(-e%7),'Target products not coefficient conjugate')
  else:sig=None;key=None
  ts.append({'id':ident(s),'beta_value':b,'products':pp,'bad_allowed':not any(pp),'signature':sig,'signature_key':key})
 check(len(rec['cases'])==18,'Incomplete candidate case list')
 for expected,claimed in zip(ts,rec['cases']):
  check(all(claimed.get(k)==v for k,v in expected.items()),'Wrong predicted product or bad-reduction condition')
 active={t['signature_key'] for t in ts if t['signature_key'] is not None}
 check(sorted(active)==rec['targets'],'Changed target signature set')
 squares={x*x%p for x in range(p)};d=next(c for c in range(1,p) if (1-4*c)%p not in squares)
 roots1=[0]*p
 for x in range(p):roots1[x*x%p]+=1
 if np is not None:
  xx,yy=np.indices((p,p),dtype=np.int64);xx=xx.ravel();yy=yy.ravel()
  aa=(xx*xx-d*yy*yy)%p;bb=(2*xx*yy+yy*yy)%p
  roots2=np.bincount(aa+p*bb,minlength=p*p)
  cc=(aa*xx-d*bb*yy)%p;ee=(aa*yy+bb*xx+bb*yy)%p
  powers=(xx,yy,cc,ee,(cc*cc-d*ee*ee)%p,(2*cc*ee+ee*ee)%p)
 else:
  roots2=[0]*(p*p);powers=[]
  for x in range(p):
   for y in range(p):
    aa=(x*x-d*y*y)%p;bb=(2*x*y+y*y)%p;roots2[aa+p*bb]+=1
    cc=(aa*x-d*bb*y)%p;ee=(aa*y+bb*x+bb*y)%p
    powers.append((x,y,cc,ee,(cc*cc-d*ee*ee)%p,(2*cc*ee+ee*ee)%p))
 base=[(x,pow(x,3,p),pow(x,6,p)) for x in range(p)]
 g=next(g for g in range(2,p) if all(pow(g,(p-1)//f,p)!=1 for f in core.distinct_factors(p-1)))
 logs={};v=1
 for i in range(p-1):logs[v]=i;v=v*g%p
 check(len(logs)==p-1,'Incomplete canonical logarithms')
 gcd3=math.gcd(3,p-1);gcd5=math.gcd(5,p-1)
 def canonical(a,b):
  if not b:return (pow(g,logs[a]%gcd5,p),0)
  e=logs[b];j=e%gcd3;mod=(p-1)//gcd3;u=((j-e)//gcd3*pow(3//gcd3,-1,mod))%mod
  return min((a*pow(g,5*(u+i*mod),p)%p,pow(g,j,p)) for i in range(gcd3))
 seventh={pow(c,7,p) for c in range(1,p)};a3=[pow(a,3,p) for a in range(p)];b5=[pow(b,5,p) for b in range(p)]
 eligible={(a,b) for a in range(p) for b in range(p) if (a3[a]+b5[b])%p in seventh}
 labels={canonical(a,b) for a,b in eligible}
 signs=[1 if (9-3*x)%p in squares else -1 for x in phis]
 check(len(set(signs))==1,'Conjugate twist mismatch');nu=signs[0]
 check((rec['Q'],rec['f'],rec['nu'])==(q,1,nu),'Wrong base/twist')
 raw={}
 for a,b in sorted(labels):
  n1=2+sum(roots1[(x6+10*b*x3+12*a*x+5*b*b)%p] for x,x3,x6 in base)
  raw[(a,b)]={'N1':n1}
 covered=set();seen=set();witness={};skip=collections.Counter();n2count=0;gcdchecks=0;rootchecks=0
 target=[p*p,-2*p*(p+1),(p+1)**2+2*p,-2*(p+1),1]
 for row_index,row in enumerate(rec['rows']):
  aa,bb=row['representative'];label=canonical(aa,bb);check(label in raw and label not in seen,'Repeated or absent curve class');seen.add(label)
  a,b=label;expected_orbit=(p-1)//(gcd3 if a==0 else gcd5 if b==0 else 1);check(row['orbit_size']==expected_orbit,'Wrong orbit size');n1=raw[label]['N1'];t=p+1-n1;S=nu*t;diff=S-2*(p+1);trace=diff//7%7 if diff%7==0 else None
  check(row['N1']==n1,'Point-count row mismatch N1');check(row['trace_correction']==trace,'Changed exact first-trace condition')
  needed=trace is not None and any(int(k.split(',')[0])==trace for k in active)
  if not needed:
   reason='trace_excludes_all_unwitnessed_targets' if active else 'all_targets_already_witnessed'
   check(row['reason']==reason and row['N2'] is None,'Unjustified omitted second count');skip[reason]+=1
   for key in ['rational_polynomial','twisted_polynomial','residual_pass','correction_pair','signature','witness_for']:check(row[key] is None,'Invented uncomputed second-degree data')
  else:
   check(row['reason']=='second_count_required' and row['N2'] is not None,'Missing required second count')
   if np is not None:
    x,y,x3,y3,x6,y6=powers
    indices=(x6+10*b*x3+12*a*x+5*b*b)%p+p*((y6+10*b*y3+12*a*y)%p)
    n2=int(2+roots2[indices].sum(dtype=np.int64))
   else:n2=2+sum(roots2[(x6+10*b*x3+12*a*x+5*b*b)%p+p*((y6+10*b*y3+12*a*y)%p)] for x,y,x3,y3,x6,y6 in powers)
   n2count+=1;check(row['N2']==n2,'Point-count row mismatch N2')
   num=t*t-p*p-1+n2;check(num%2==0,'Nonintegral Newton coefficient');B=num//2
   rp=[p*p,-p*t,B,-t,1];P=[p*p,-p*S,B,-S,1]
   res=all((x-y)%7==0 for x,y in zip(P,target))
   check(row['rational_polynomial']==rp and row['twisted_polynomial']==P and row['residual_pass']==res,'Wrong reconstructed Frobenius polynomial')
   key=None
   if res:
    tn=S-2*(p+1);nn=B-2*p-(p+1)*S+(p+1)**2
    check(tn%7==0 and nn%49==0,'Nonintegral trace/norm correction')
    sig=[tn//7%7,nn//49%7];pair=[]
    for c in range(7):
     for e in range(7):
      rootchecks+=1
      if (2*c+e-sig[0])%7==0 and (c*c+c*e-e*e-sig[1])%7==0:pair.append(wcode((c,e)))
    check(pair and sorted(pair)==row['correction_pair'] and sig==row['signature'],'Wrong coefficient trace/norm pair')
    k=f'{sig[0]},{sig[1]}'
    if k in active:active.remove(k);witness[k]=row_index;key=k
   else:check(row['correction_pair'] is None and row['signature'] is None,'Invented residual correction pair')
   check(row['witness_for']==key,'False target witness')
  for a0,b0 in row['admissible_pairs']:
   check((a0,b0) in eligible and (a0,b0) not in covered,'Admissible-pair overlap or false pair');covered.add((a0,b0))
   check(canonical(a0,b0)==label,'Wrong weighted curve assignment');check(core.smooth(a0,b0,p),'Singular good curve');gcdchecks+=1
 check(covered==eligible and seen==labels,'Incomplete admissible curve coverage')
 dig=hashlib.sha256()
 for a,b in sorted(eligible):dig.update(f'{a},{b}\n'.encode())
 check(rec['admissible_pairs']==len(eligible) and rec['pair_set_sha256']==dig.hexdigest(),'Changed equation-pair totals/digest')
 check(rec['degree_one_counts']==len(labels) and rec['degree_two_counts']==n2count,'Changed count coverage')
 check(rec['skip_reasons']==dict(skip) and rec['unattained_targets']==sorted(active) and rec['witness_rows']==witness,'Changed target existence classification')
 cases=[]
 for t in ts:
  t=dict(t);k=t['signature_key'];t['good_witness_row']=witness.get(k);t['good_exists']=k in witness if k is not None else None;t['survives']=t['bad_allowed'] or bool(t['good_exists']);cases.append(t)
 check(cases==rec['cases'],'Changed candidate cases');ids=[c['id'] for c in cases if c['survives']];check(ids==rec['survivors'],'Changed target survivor list')
 return {'q':q,'status':'PASS_SEPARATE_TARGET_AUDIT','admissible_pairs':len(eligible),'degree_one_counts':len(labels),'degree_two_counts':n2count,'smoothness_checks':gcdchecks,'coefficient_root_checks':rootchecks,'skip_reasons':dict(skip),'cases':cases,'survivors':ids,'unattained_targets':sorted(active),'primary_arithmetic_imports':False,'arithmetic':'Different residue field, explicit square-root counts, discrete-log curve canonicalization, trace/norm coefficient extraction'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--counts',type=Path,required=True);p.add_argument('--sieve',type=Path,required=True);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--columns',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 load=lambda x:json.loads(x.read_text());result=audit(load(a.counts),load(a.sieve),load(a.fixture),load(a.columns));a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('PASS_SEPARATE_TARGET_AUDIT',result['q'],len(result['survivors']),flush=True)
if __name__=='__main__':main()
