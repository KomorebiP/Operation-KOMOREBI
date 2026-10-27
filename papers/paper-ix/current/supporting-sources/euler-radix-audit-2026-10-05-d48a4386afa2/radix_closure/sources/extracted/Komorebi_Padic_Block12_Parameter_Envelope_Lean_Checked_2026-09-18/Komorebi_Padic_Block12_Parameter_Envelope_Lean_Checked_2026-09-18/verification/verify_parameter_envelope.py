#!/usr/bin/env python3
"""Independent exact finite audit for Komorebi p-adic Block 12.

The universal claims are proved in Lean.  This script checks totalized boundary
cases, exact auxiliary elimination, monotonic transport, and concrete compiler
instances using Python arbitrary-precision integers.
"""
from __future__ import annotations
import hashlib,json,platform,sys,time
from collections import Counter
from pathlib import Path
from verify_final_fiber_boundary import concrete_boundary

P_MAX=160
R_MAX=600
H_MAX=15
MONO_P_MAX=128
MONO_K_MAX=50_000
COMPILER_PRIMES=(2,3,5,7,11,13)
COMPILER_R_MAX=150
COMPILER_H_MAX=7
STRESS_PARAMETER_CASES=(
 (0,10**12+17,37),(1,10**12+19,41),(2,10**15+123,0),
 (3,10**18+77,5),(97,10**24+987654321,31),(997,10**30+12345,1024),
)
COMPILER_STRESS_CASES=((2,8059,0),(2,12000,3),(3,5000,0),(5,4000,1),(7,3500,2),(13,3000,0))

def nsub(a:int,b:int)->int:return max(a-b,0)
def ndiv(a:int,b:int)->int:return 0 if b==0 else a//b
def coarse_k(r:int,h:int)->int:return ndiv(nsub(r,1),h+1)
def qbound(p:int,r:int,h:int)->int:return ndiv(coarse_k(r,h),nsub(p,1))+1
def block_depth(p:int,B:int)->int:return ndiv(nsub(B,1),p)
def direct_depth(p:int,r:int,h:int)->int:return ndiv(coarse_k(r,h),p*nsub(p,1))
def envelope_core(p:int,K:int)->int:
 d=ndiv(K,p*nsub(p,1))
 return 2*(ndiv(K,nsub(p,1))+1)+p+(p*d*(d+1))//2
def parameter_bound(p:int,r:int,h:int)->int:return envelope_core(p,coarse_k(r,h))
def raw_bound(p:int,r:int)->int:return envelope_core(p,nsub(r,1))
def prime_envelope(p:int,r:int,h:int)->int:
 B=qbound(p,r,h); d=block_depth(p,B)
 return 2*B+p+(p*d*(d+1))//2

def sha256(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def main()->int:
 started=time.perf_counter(); root=Path(__file__).resolve().parents[1]
 counts=Counter(); failures=[]; maxima={'parameter_bound':{'value':0,'case':None},'raw_gap':{'value':0,'case':None},'depth':{'value':0,'case':None}}
 def check(name:str,ok:bool,**data):
  counts[name]+=1
  if not ok and len(failures)<200:failures.append({'check':name,**data})
 def record(name:str,value:int,case):
  if value>maxima[name]['value']:maxima[name]={'value':value,'case':case}

 # Dense totalized grid, including p=0 and p=1.
 for p in range(P_MAX+1):
  for r in range(R_MAX+1):
   raw=raw_bound(p,r)
   for h in range(H_MAX+1):
    K=coarse_k(r,h); B=qbound(p,r,h); d1=block_depth(p,B); d2=direct_depth(p,r,h); param=parameter_bound(p,r,h); prime=prime_envelope(p,r,h)
    case={'p':p,'r':r,'h':h}
    check('search_bound_sub_one',nsub(B,1)==ndiv(K,nsub(p,1)),**case)
    check('depth_exact',d1==d2,**case)
    check('proposed_depth_inequality',d1<=d2,**case)
    check('prime_eq_parameter',prime==param,**case)
    check('coarseK_le_r_sub_one',K<=nsub(r,1),**case)
    check('parameter_le_raw',param<=raw,**case)
    if p==0:check('zero_base_depth',d2==0,**case)
    if p==1:check('one_base_depth',d2==0,**case)
    record('parameter_bound',param,case);record('raw_gap',raw-param,case);record('depth',d2,case)

 # Independent adjacent monotonicity lane for the core envelope.
 for p in range(MONO_P_MAX+1):
  prev=envelope_core(p,0)
  for K in range(1,MONO_K_MAX+1):
   cur=envelope_core(p,K)
   check('core_adjacent_monotone',prev<=cur,p=p,K=K)
   prev=cur

 stress_parameter=[]
 for p,r,h in STRESS_PARAMETER_CASES:
  K=coarse_k(r,h);B=qbound(p,r,h);d1=block_depth(p,B);d2=direct_depth(p,r,h);param=parameter_bound(p,r,h);raw=raw_bound(p,r)
  check('stress_depth_exact',d1==d2,p=p,r=r,h=h)
  check('stress_prime_eq_parameter',prime_envelope(p,r,h)==param,p=p,r=r,h=h)
  check('stress_parameter_le_raw',param<=raw,p=p,r=r,h=h)
  stress_parameter.append({'p':p,'r':r,'h':h,'coarseK':K,'quotient_bound':B,'depth':d2,'parameter_bound':param,'raw_precision_bound':raw})

 compiler_records=[]
 def audit_compiler(p:int,r:int,h:int,lane:str):
  out=concrete_boundary(p,r,h); total=out['quotient']+out['boundary_tests']+out['representative_tests'];param=parameter_bound(p,r,h);raw=raw_bound(p,r)
  counts[f'{lane}_compiler_cases']+=1
  check('compiler_total_le_parameter',total<=param,lane=lane,p=p,r=r,h=h)
  check('compiler_total_le_raw',total<=raw,lane=lane,p=p,r=r,h=h)
  check('compiler_prime_eq_parameter',prime_envelope(p,r,h)==param,lane=lane,p=p,r=r,h=h)
  check('compiler_depth_exact',block_depth(p,qbound(p,r,h))==direct_depth(p,r,h),lane=lane,p=p,r=r,h=h)
  if lane=='stress':compiler_records.append({'p':p,'r':r,'h':h,'quotient':out['quotient'],'layer':out['layer'],'exact_total':total,'parameter_bound':param,'raw_precision_bound':raw,'depth':direct_depth(p,r,h)})
 for p in COMPILER_PRIMES:
  for r in range(1,COMPILER_R_MAX+1):
   for h in range(COMPILER_H_MAX+1):audit_compiler(p,r,h,'grid')
 for args in COMPILER_STRESS_CASES:audit_compiler(*args,lane='stress')

 source=sorted((root/'lean'/'KomorebiPadic').glob('*.lean'))
 report={'schema':'komorebi-padic-block12-parameter-envelope-audit-v1','status':'PASS' if not failures else 'FAIL','generated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'parameters':{'p_range':[0,P_MAX],'r_range':[0,R_MAX],'h_range':[0,H_MAX],'monotonicity_p_range':[0,MONO_P_MAX],'monotonicity_K_range':[0,MONO_K_MAX],'compiler_primes':list(COMPILER_PRIMES),'compiler_r_max':COMPILER_R_MAX,'compiler_h_max':COMPILER_H_MAX,'stress_parameter_cases':[list(x) for x in STRESS_PARAMETER_CASES],'compiler_stress_cases':[list(x) for x in COMPILER_STRESS_CASES]},'counts':dict(sorted(counts.items())),'total_recorded_checks_and_cases':sum(counts.values()),'failure_count':len(failures),'failures':failures,'maxima':maxima,'stress_parameter_records':stress_parameter,'compiler_stress_records':compiler_records,'source_sha256':{str(p.relative_to(root)):sha256(p) for p in source},'runtime_seconds':time.perf_counter()-started,'platform':platform.platform(),'python':sys.version,'non_claims':['Finite audit output is not the universal proof.','The parameter and raw-precision expressions are upper bounds, not exact operation counts in general.','No asymptotic optimality or novelty claim is made.','The end-to-end compiler theorem remains restricted to prime bases and positive precision.']}
 out=root/'results'/'parameter_envelope_audit.json';out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':report['status'],'total_checks':report['total_recorded_checks_and_cases'],'failures':len(failures),'maxima':maxima,'runtime_seconds':report['runtime_seconds'],'output':str(out)},indent=2,sort_keys=True))
 return 0 if not failures else 1
if __name__=='__main__':raise SystemExit(main())
