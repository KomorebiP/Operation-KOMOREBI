#!/usr/bin/env python3
"""Replay of finite certificates and orthogonal arithmetic checks.
Universal implication is justified separately in PROOF_AND_BOUNDARY.md.
"""
from __future__ import annotations
import hashlib,json,math,platform,time
from collections import Counter
from pathlib import Path
import fast_parameter_certificate as f
import build_parameter_certificate as b
base=f.base
ROOT=Path(__file__).resolve().parent
C=Counter()
def check(ok,label):
 if not ok:raise AssertionError(label)
 C[label]+=1

def source_log(P):
 M=1<<P;u=0
 for k in range(1,P+10):
  vk=b.val(k,P+10);v=3*(k-1)-vk
  if v<P:
   term=(pow(k>>vk,-1,M)<<v)%M
   u=(u+(-term if k%2==0 else term))%M
 check(u%2==1,'log9 divided by 8 is unit')
 coeff=[];odd=1;vf=0
 for m in range(P+1):
  n=m+1;v=b.val(n,P+10);vf+=v;odd=odd*(n>>v)%M
  w=3*m-vf
  cm=(pow(u,m+1,M)*pow(odd,-1,M)<<w)%M if w<P else 0
  coeff.append(cm)
 while coeff and coeff[-1]==0:coeff.pop()
 shifted=base.shift(coeff,1,M)
 return base.mul(shifted,[pow(-2,n,M) for n in range(P)],M)[:P]

def audit():
 started=time.time();base.B=base.bernoullis(629)
 # Bernoulli recurrence and fast unit-factor computation use different binomial routes.
 for n in range(2,98,2):
  for P in [16,40,80]:
   check(f.fast_twoB(n,P)==base.fmod(2*base.B[n],P),'small Bernoulli exact rational equality')
 original=base.twoB
 for q in [0,1,160,161,162]:
  n=2*((1<<640)-161+q)
  for P in [40,96]:
   check(original(n,P)==f.fast_twoB(n,P),'large Bernoulli exact-binomial versus unit-binomial')
 for P in [64,272,629]:
  a=list(base.source(P));c=source_log(P)
  for x,y in zip(a,c):check(x==y,'Newton source versus logarithmic source coefficient')
  check(len(a)==len(c),'source lengths')
 data=[]
 for name in ['parameter_certificate_272.json','fast_final_certificate_272.json','fast_certificate_512.json','fast_certificate_629.json']:
  d=json.loads((ROOT/name).read_text());data.append(d)
  P=d['global_precision'];N=d['joint_precision'];mod=1<<N
  H0,H1=[list(map(int,d[k])) for k in ['H0','H1']]
  (t,z),Q0,Q1,trace=b.lift_joint(H0,H1,N)
  check((t,z)==(int(d['candidate_T_residue']),int(d['candidate_Z_residue'])),'joint lift recomputed')
  check(Q0==list(map(int,d['Q0'])) and Q1==list(map(int,d['Q1'])),'half derivative coefficients')
  check(trace==d['joint_lift_trace'],'all binary lift stages')
  check(t>0 and t<mod,'canonical nonzero candidate')
  for row in trace:
   m=1<<row['bits'];tt=int(row['T']);zz=int(row['Z'])
   check((base.ev(H0,zz,m)+tt*base.ev(H1,zz,m))%m==0,'joint value residue')
   check((base.ev(Q0,zz,m)+tt*base.ev(Q1,zz,m))%m==0,'joint half-slope residue')
 # Compare global-first implementation with local-first arithmetic at all shared bits.
 ref=data[0]
 for d in data[1:]:
  for key,content in [('H0',178),('H1',178),('cubic_H0',162),('cubic_H1',162)]:
   aa=list(map(int,ref[key]));cc=list(map(int,d[key]));M=1<<(272-content)
   for i in range(max(len(aa),len(cc))):
    check((aa[i] if i<len(aa) else 0)%M==(cc[i] if i<len(cc) else 0)%M,'global-first/local-first coefficient equality')
  check(int(d['candidate_T_residue'])%(1<<93)==int(ref['candidate_T_residue']),'shared parameter digits')
 final=data[-1];tau=int(final['candidate_T_residue'])
 check(final['joint_precision']==450 and tau >= (1<<449),'height nonintersection inequality')
 # Exhaustive finite skeleton/carry interfaces, not samples of the huge input range.
 e=[3*q+160 .bit_count()-(160-q).bit_count() for q in range(161)]
 check(min(e)==-1 and [q for q,x in enumerate(e) if x==-1]==[1],'unique lower carry minimum')
 cover=[0]*256
 for i in range(161):
  k=max(i,160-i).bit_length()
  for residue in range(i,256,1<<k):cover[residue]+=1
 check(cover==[1]*256,'canonical 161-ball partition')
 check(90 .bit_count()==4 and 70 .bit_count()==3 and 90-4+70-3==153,'resonant slope at 90')
 # For T<2^449, b<2^467, so s2(r)<=1104 and the global carry cutoff<=367.
 check((1104-1)//3==367,'uniform bounded-height carry cutoff')
 for q in range(162,368):check(3*(q-161)+(q-161).bit_count()>0,'postterminal strict carry increment')
 # Fresh actual-input checks at small, deep, and maximal-height parameters.
 base.twoB=f.fast_twoB;P=272;M=1<<P;src=list(base.source(P));ref=data[1]
 H0=list(map(int,ref['H0']));H1=list(map(int,ref['H1']));localM=1<<(P-178)
 point_records=[]
 for T in [0,1,718787533,(1<<449)-1]:
  B=17659+(1<<18)*T;r=(B<<640)-161
  costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range((r.bit_count()-1)//3+1)]
  mu=min(costs);j=max(q for q,x in enumerate(costs) if x==mu)
  check((mu,j)==(-154,161),'fresh actual terminal identification')
  Q=(P+r.bit_count()+mu-2)//3;gam=base.gamma(r,mu,P,Q)
  lo,hi=f.local_split(P,10202,15,gam,src)
  G=[(x+y)%M for x,y in zip(lo,hi)]
  check(all(x%(1<<178)==0 for x in G),'fresh actual deep content lower bound')
  coef=[((x>>178)*B)%localM for x in G]
  target=[(x+T*y)%localM for x,y in zip(H0,H1)]
  for i in range(max(len(coef),len(target))):
   check((coef[i] if i<len(coef) else 0)==(target[i] if i<len(target) else 0),'fresh actual versus uniform coefficient template')
  point_records.append({'T':str(T),'B':str(B),'mu':mu,'j':j,'precision':P})
 # A legitimate positive singular parameter must remain in the certificate.
 for t0 in [0,1,27,65535]:
  (tt,zz),_,_,_=b.lift_joint([-t0,0,1],[1,0,0],16)
  check((tt,zz)==(t0,0),'planted positive singular parameter retained')
 result={'status':'passed','registered_checks':sum(C.values()),'counts':dict(C),
  'main_claim':'all T in [0,2^449) give no critical zero anywhere in Z2 for r=(17659+2^18*T)*2^640-161, conditional on the explicitly cited inherited wall and finite-template theorems',
  'actual_input_cross_checks':point_records,'seconds':time.time()-started,'python':platform.python_version(),
  'scope':'exact finite computations plus separate proof of uniform implication; no new Lean kernel verification',
  'source_independence':'source Newton/log implementations independent; gamma formula and Bernoulli recurrence remain inherited, with alternate binomial arithmetic checked',
  'failures':['Streaming exec unavailable; no process started','Slow global-first precision512 exceeded 60 seconds; no completed result',
  'Initial local-first precision512 with giant binomials exceeded45 seconds; replaced by odd-unit/valuation binomial evaluation; final runs completed'],
  'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 out=ROOT/'VERIFICATION.json';out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':audit()
