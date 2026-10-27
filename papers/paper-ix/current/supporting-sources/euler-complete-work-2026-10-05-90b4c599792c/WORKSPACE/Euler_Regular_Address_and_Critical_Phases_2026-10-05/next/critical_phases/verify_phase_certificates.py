#!/usr/bin/env python3
"""Independent source/gamma construction and direct-binomial leaf verification."""
from pathlib import Path
from math import comb
from fractions import Fraction
import sys,json,hashlib,time,platform
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
import dyadic_modular as d

def direct_affine(a,s,h,M):
 deg=min(len(a)-1,(M.bit_length()-2)//max(1,(h&-h).bit_length()-1)) if h%2==0 else len(a)-1
 return d.trim([sum(a[n]*comb(n,i)*pow(s,n-i,M) for n in range(i,len(a)))*pow(h,i,M)%M for i in range(deg+1)])

def val(n):return 100000 if n==0 else (abs(n)&-abs(n)).bit_length()-1

def leaf_check(p0,p1,P,atlas,paired):
 assert sum((Fraction(1,1<<a['k']) for a in atlas),Fraction())==1
 for i,a in enumerate(atlas):
  assert a['kind'] in ('constant','simple_root')
  for b in atlas[:i]:assert (a['s']-b['s'])%(1<<min(a['k'],b['k']))
  c=a.get('value',a.get('content'));M=1<<(c+1)
  coeffs=[direct_affine(p,a['s'],1<<a['k'],M) for p in ([p0,p1] if paired else [p0])]
  assert all(z%(1<<c)==0 for p in coeffs for z in p)
  red=[d.trim([z>>c for z in p]) for p in coeffs]
  expected=[a['red0'],a['red1']] if paired else [a['reduction']]
  assert red==expected
  if a['kind']=='constant':assert red[0]==[1] and (not paired or red[1]==[0])
  else:assert len(red[0])==2 and red[0][1]==1 and (not paired or len(red[1])==1)

started=time.time();checks=[]
for L in(639,640,641):
 p=ROOT/f'phase_{L}.json';rec=json.loads(p.read_text());t=rec['template'];P=t['precision'];M=1<<P;r=(1<<L)-161
 for name,hash0 in rec['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==hash0
 assert P<=L+1-(2*(161+2*P)).bit_length()
 assert 3*(t['computed_qmax']+1)+1-r.bit_count()-t['mu']>=P
 gam=[d.gamma_mod(r,q,t['mu'],P) for q in range(t['computed_qmax']+1)]
 assert gam==rec['gamma']
 assert d.trim(d.source_polynomial(P))==d.trim(rec['source'])
 assert rec['lower_V_mod128']==[2,19,84,16,32,64]
 low=t['low'];high=t['high']
 if L!=640:
  c=rec['certificates'][0];assert c['parameter_residue']==1 and c['parameter_exponent']==1
  f0=d.add(low,high,M);f1=[2*z%M for z in low]
  leaf_check(f0,f1,P,c['atlas'],True)
  assert sum(a['kind']=='simple_root' for a in c['atlas'])=={639:1,641:3}[L]
 else:
  N=P-160;m=1<<N
  als=[direct_affine(p,90,128,M) for p in(low,high)]
  assert all(z%(1<<160)==0 for p in als for z in p)
  A,C=([z>>160 for z in p] for p in als)
  assert d.trim(A)==d.trim(rec['low_local']) and d.trim(C)==d.trim(rec['high_local'])
  W=d.add(d.mul(A,[i*C[i] for i in range(1,len(C))],m),[-z for z in d.mul(C,[i*A[i] for i in range(1,len(A))],m)],m)
  assert W==rec['wronskian'];leaf_check(W,None,N,rec['wronskian_atlas'],False)
  # Independent binary lift of W(1+2Z)/16 to60bits.
  odd=direct_affine(W,1,2,m);assert all(z%16==0 for z in odd)
  odd=[z//16 for z in odd];z=0
  for bits in range(1,N-3):
   mm=1<<bits
   choices=[zz for zz in(z,z+(1<<(bits-1))) if d.evaluate(odd,zz,mm)==0]
   assert len(choices)==1;z=choices[0]
  y=1+2*z;assert y==rec['candidate_Y']
  mm=1<<61;assert d.evaluate(A,y,mm)%2
  b=-d.evaluate(C,y,mm)*pow(d.evaluate(A,y,mm),-1,mm)%mm
  assert b==rec['candidate_B'] and b%(1<<18)==17659
  assert (90+128*y)%32768==10202
 checks.append({'L':L,'independent_gamma_coefficients':len(gam),'independent_source_coefficients':len(rec['source']),'direct_binomial_leaf_verification':'passed','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
result={'status':'passed','checks':checks,'arithmetic':'exact integers and Fractions, no floating point','python':platform.python_version(),'seconds':time.time()-started,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'nonclaims':['Inherited uniform-template theorem is a mathematical dependency','No full global Euler simplicity','No new Lean compilation']}
(ROOT/'VERIFICATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
